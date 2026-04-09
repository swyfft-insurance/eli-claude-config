#!/usr/bin/env python3
"""Fetch a YouTrack ticket with description, comments, custom fields, and images."""

import sys
import os
import json
import re
import subprocess
import tempfile
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

YOUTRACK_BASE = "https://swyfft.myjetbrains.com/youtrack"

# Custom fields worth extracting (skip noise like "Numeric Priority")
RELEVANT_FIELDS = {
    "Stage", "Priority", "IssueType", "Release Stage", "ProductLine",
    "Carrier", "RatingType", "USState", "Assignee", "QA Assignee",
    "Business Owner", "Found in Stage", "Platform", "Effort",
}


def get_api_token():
    """Get YouTrack API token. Prefer pwsh (bash truncates base64 '=' chars)."""
    # Windows user-level env var via pwsh — avoids bash truncation of '=' in base64
    try:
        result = subprocess.run(
            [
                "pwsh", "-NoProfile", "-Command",
                "[System.Environment]::GetEnvironmentVariable('YOUTRACK_API_TOKEN', 'User')",
            ],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    # Fallback to process environment (works on Linux/CI)
    token = os.environ.get("YOUTRACK_API_TOKEN")
    if token:
        return token
    print("ERROR: YOUTRACK_API_TOKEN not found in env or Windows user variables", file=sys.stderr)
    sys.exit(1)


def api_get(path, token):
    """GET from the YouTrack REST API. `path` starts with /api/..."""
    url = f"{YOUTRACK_BASE}{path}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def download_file(relative_url, dest_path, token):
    """Download a file from YouTrack using a relative URL."""
    url = f"{YOUTRACK_BASE.rstrip('/youtrack')}{relative_url}"
    # The relative URL already starts with /youtrack/api/files/...
    if relative_url.startswith("/youtrack"):
        url = f"https://swyfft.myjetbrains.com{relative_url}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as resp:
        with open(dest_path, "wb") as f:
            f.write(resp.read())


def format_timestamp(ts_ms):
    """Convert millisecond timestamp to readable UTC string."""
    if not ts_ms:
        return None
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def extract_user(user_obj):
    """Pull a display name from a user object."""
    if not user_obj:
        return None
    if isinstance(user_obj, dict):
        return user_obj.get("name") or user_obj.get("login")
    return str(user_obj)


def extract_custom_fields(raw_fields):
    """Extract relevant custom fields into a flat dict."""
    out = {}
    for cf in raw_fields or []:
        name = cf.get("name", "")
        if name not in RELEVANT_FIELDS:
            continue
        value = cf.get("value")
        if value is None:
            out[name] = None
        elif isinstance(value, dict):
            out[name] = value.get("name") or value.get("login") or value.get("text")
        elif isinstance(value, list):
            out[name] = [
                v.get("name", str(v)) if isinstance(v, dict) else str(v)
                for v in value
            ]
        else:
            out[name] = value
    return out


def download_images(attachments, images_dir, token):
    """Download image attachments, returning {filename: local_path} map."""
    downloaded = {}
    seen_names = set()
    for att in attachments:
        mime = att.get("mimeType", "")
        if not mime.startswith("image/"):
            continue
        name = att.get("name", "unknown.png")
        dest = images_dir / name
        # Deduplicate filenames
        if name in seen_names:
            stem = dest.stem
            suffix = dest.suffix
            i = 2
            while dest.exists():
                dest = images_dir / f"{stem}_{i}{suffix}"
                i += 1
        seen_names.add(name)
        try:
            download_file(att["url"], str(dest), token)
            downloaded[name] = str(dest)
        except Exception as e:
            downloaded[name] = f"DOWNLOAD_FAILED: {e}"
    return downloaded


def resolve_images(text, image_map):
    """Replace ![alt](filename){width=...} in markdown with [IMAGE: local_path] markers.

    This makes it obvious exactly where each image appears in the text,
    so Claude can read each image in context rather than cross-referencing
    a separate map.
    """
    def replace_match(m):
        alt = m.group(1)
        filename = m.group(2).split("/")[-1]  # strip any path prefix
        local_path = image_map.get(filename)
        if local_path and not local_path.startswith("DOWNLOAD_FAILED"):
            if alt:
                return f"[IMAGE ({alt}): {local_path}]"
            return f"[IMAGE: {local_path}]"
        return m.group(0)  # leave unchanged if not downloaded

    # Match ![alt](filename) optionally followed by {width=...}
    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)(?:\{[^}]*\})?", replace_match, text)


def main():
    if len(sys.argv) < 2:
        print("Usage: read-ticket.py <ISSUE-ID>", file=sys.stderr)
        sys.exit(1)

    issue_id = sys.argv[1].upper()
    token = get_api_token()

    # Output directory
    output_dir = Path(tempfile.gettempdir()) / "swyfft-tickets" / issue_id
    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / "images"
    images_dir.mkdir(exist_ok=True)

    # --- Fetch issue ---
    issue_fields = ",".join([
        "id", "idReadable", "summary", "description",
        "reporter(login,name)", "created", "updated", "resolved",
        "customFields(name,value(name,login,text))",
        "attachments(id,name,mimeType,size,url)",
        "links(direction,linkType(name),issues(idReadable,summary))",
    ])
    issue = api_get(
        f"/api/issues/{issue_id}?fields={urllib.parse.quote(issue_fields, safe='(),*')}",
        token,
    )

    # --- Fetch all comments (paginated) ---
    comments = []
    comment_fields = "id,text,author(login,name),created,updated,attachments(id,name,mimeType,size,url)"
    skip = 0
    while True:
        batch = api_get(
            f"/api/issues/{issue_id}/comments?fields={urllib.parse.quote(comment_fields, safe='(),*')}&$top=50&$skip={skip}",
            token,
        )
        if not batch:
            break
        comments.extend(batch)
        if len(batch) < 50:
            break
        skip += 50

    # --- Download images ---
    all_attachments = list(issue.get("attachments") or [])
    for c in comments:
        all_attachments.extend(c.get("attachments") or [])
    # Deduplicate by attachment id
    seen_ids = set()
    unique_attachments = []
    for att in all_attachments:
        aid = att.get("id")
        if aid and aid not in seen_ids:
            seen_ids.add(aid)
            unique_attachments.append(att)
    downloaded = download_images(unique_attachments, images_dir, token)

    # --- Build output ---
    description_raw = issue.get("description", "")
    description_resolved = resolve_images(description_raw, downloaded)

    output = {
        "id": issue.get("idReadable", issue_id),
        "summary": issue.get("summary", ""),
        "url": f"https://swyfft.myjetbrains.com/youtrack/issue/{issue_id}",
        "reporter": extract_user(issue.get("reporter")),
        "created": format_timestamp(issue.get("created")),
        "updated": format_timestamp(issue.get("updated")),
        "resolved": format_timestamp(issue.get("resolved")),
        "customFields": extract_custom_fields(issue.get("customFields")),
        "links": [],
        "description": description_resolved,
        "comments": [],
        "images": downloaded,
        "imagesDir": str(images_dir),
    }

    # Links
    for link in issue.get("links") or []:
        direction = link.get("direction", "")
        link_type = (link.get("linkType") or {}).get("name", "")
        for linked in link.get("issues") or []:
            output["links"].append({
                "type": link_type,
                "direction": direction,
                "id": linked.get("idReadable"),
                "summary": linked.get("summary"),
            })

    # Comments — resolve image references inline
    for c in comments:
        comment_text = c.get("text", "")
        output["comments"].append({
            "author": extract_user(c.get("author")),
            "created": format_timestamp(c.get("created")),
            "text": resolve_images(comment_text, downloaded),
        })

    # Write JSON to file
    output_file = output_dir / "ticket.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Print to stdout
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
