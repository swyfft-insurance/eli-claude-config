#!/usr/bin/env python3
"""Gather standup data from GitHub and YouTrack, organized by day.

Outputs structured JSON with work items attributed to correct days
based on actual timestamps (commits, YouTrack activities), filtered
to only Eli's work. Claude formats the output; this script handles
the data gathering and day attribution deterministically.
"""

import sys
import os
import json
import re
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta, tzinfo
import calendar

YOUTRACK_BASE = "https://swyfft.myjetbrains.com/youtrack"
GITHUB_REPO = "swyfft-insurance/swyfft_web"
GITHUB_USER = "eli-swyfft"
YOUTRACK_LOGIN = "eli.koslofsky"

# Stdlib-only US Eastern timezone (no tzdata/pytz dependency)
_EST = timezone(timedelta(hours=-5), "EST")
_EDT = timezone(timedelta(hours=-4), "EDT")

def _is_dst(dt_utc):
    """Check if a UTC datetime falls in US Eastern Daylight Time.
    DST: second Sunday of March 2:00 AM ET → first Sunday of November 2:00 AM ET.
    """
    year = dt_utc.year
    # Second Sunday of March: find first day of March, advance to first Sunday, add 7
    mar1 = datetime(year, 3, 1, tzinfo=timezone.utc)
    dst_start = mar1 + timedelta(days=(6 - mar1.weekday()) % 7 + 7)  # second Sunday
    dst_start = dst_start.replace(hour=7)  # 2 AM EST = 7 AM UTC
    # First Sunday of November
    nov1 = datetime(year, 11, 1, tzinfo=timezone.utc)
    dst_end = nov1 + timedelta(days=(6 - nov1.weekday()) % 7)  # first Sunday
    dst_end = dst_end.replace(hour=6)  # 2 AM EDT = 6 AM UTC
    return dst_start <= dt_utc < dst_end

def to_et(dt_utc):
    """Convert a UTC-aware datetime to US Eastern."""
    if dt_utc is None:
        return None
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)
    utc = dt_utc.astimezone(timezone.utc)
    tz = _EDT if _is_dst(utc) else _EST
    return utc.astimezone(tz)


# ── Helpers ──────────────────────────────────────────────────────────

def die(msg):
    print(json.dumps({"error": msg}))
    sys.exit(1)


def get_youtrack_token():
    # pwsh first — bash truncates base64 '=' characters
    try:
        r = subprocess.run(
            ["pwsh", "-NoProfile", "-Command",
             "[System.Environment]::GetEnvironmentVariable('YOUTRACK_API_TOKEN', 'User')"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    token = os.environ.get("YOUTRACK_API_TOKEN")
    if token:
        return token
    die("YOUTRACK_API_TOKEN not found")


def yt_get(path, token):
    url = f"{YOUTRACK_BASE}{path}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"WARN: YouTrack GET {path[:80]}... failed: {e}", file=sys.stderr)
        return []


def gh_json(*args):
    cmd = ["gh"] + list(args)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30, encoding="utf-8", errors="replace")
    except FileNotFoundError:
        die("gh CLI not found on PATH")
    if r.returncode != 0:
        print(f"WARN: gh {' '.join(args[:4])}... failed: {r.stderr.strip()[:200]}", file=sys.stderr)
        return []
    if not r.stdout.strip():
        return []
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return []


def iso_to_et(s):
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return to_et(dt)
    except ValueError:
        return None


def ms_to_et(ms):
    if not ms:
        return None
    return to_et(datetime.fromtimestamp(ms / 1000, tz=timezone.utc))


def to_date(dt):
    return dt.date() if dt else None


def last_working_day(today):
    d = today - timedelta(days=1)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def extract_tickets(text):
    return sorted(set(re.findall(r"SW-\d+", text or "", re.IGNORECASE)))


def yt_url(ticket_id):
    return f"https://swyfft.myjetbrains.com/youtrack/issue/{ticket_id}"


def gh_pr_url(number):
    return f"https://github.com/{GITHUB_REPO}/pull/{number}"


def extract_yt_field(issue, field_name):
    for cf in issue.get("customFields", []):
        if cf.get("name") == field_name:
            val = cf.get("value")
            if isinstance(val, dict):
                return val.get("name")
            if isinstance(val, list):
                return ", ".join(v.get("name", str(v)) for v in val if isinstance(v, dict))
            return val
    return None


def activity_value_names(val):
    """Extract name(s) from a YouTrack activity added/removed value."""
    if val is None:
        return []
    if isinstance(val, list):
        return [v.get("name") for v in val if isinstance(v, dict) and v.get("name")]
    if isinstance(val, dict):
        name = val.get("name")
        return [name] if name else []
    if isinstance(val, str):
        return [val]
    return []


# ── Data Gathering ───────────────────────────────────────────────────

def gather_github_prs(lwd):
    """Fetch PRs updated since last working day, with details."""
    search_date = lwd.isoformat()

    # Two sources to get full data (search has state filter, list has mergedAt)
    prs_search = gh_json(
        "search", "prs",
        f"--author={GITHUB_USER}",
        f"--updated=>={search_date}",
        f"--repo={GITHUB_REPO}",
        "--json", "number,title,state,createdAt,updatedAt,url",
        "--limit", "30",
    )
    prs_list = gh_json(
        "pr", "list",
        f"--author={GITHUB_USER}",
        f"--repo={GITHUB_REPO}",
        "--state", "all",
        "--json", "number,title,state,createdAt,updatedAt,mergedAt,url,headRefName",
        "--limit", "20",
    )

    # Merge by PR number (list has mergedAt + headRefName)
    pr_map = {}
    for pr in prs_search + prs_list:
        num = pr.get("number")
        if not num:
            continue
        if num not in pr_map:
            pr_map[num] = pr
        else:
            pr_map[num].update({k: v for k, v in pr.items() if v})

    # Filter to updated in window
    relevant = {}
    for num, pr in pr_map.items():
        updated = iso_to_et(pr.get("updatedAt"))
        if updated and to_date(updated) >= lwd:
            relevant[num] = pr

    # Fetch details (commits, reviews) for each
    for num in relevant:
        detail = gh_json(
            "pr", "view", str(num),
            f"--repo={GITHUB_REPO}",
            "--json", "commits,reviews",
        )
        if detail:
            relevant[num]["_commits"] = detail.get("commits", [])
            relevant[num]["_reviews"] = detail.get("reviews", [])

    return relevant


def gather_youtrack(yt_token, lwd, today):
    """Fetch YouTrack issues and activities."""
    fields = "idReadable,summary,customFields(name,value(name))"

    # Query 1: recently updated
    q1 = f"assignee: me updated: {lwd.isoformat()} .. {today.isoformat()}"
    issues1 = yt_get(
        f"/api/issues?query={urllib.parse.quote(q1)}&fields={urllib.parse.quote(fields, safe='(),*')}&$top=50",
        yt_token,
    )

    # Query 2: currently active
    q2 = "assignee: me Stage: Develop, Review"
    issues2 = yt_get(
        f"/api/issues?query={urllib.parse.quote(q2)}&fields={urllib.parse.quote(fields, safe='(),*')}&$top=50",
        yt_token,
    )

    # Deduplicate
    all_issues = {}
    for issue in (issues1 or []) + (issues2 or []):
        iid = issue.get("idReadable")
        if iid:
            all_issues[iid] = issue

    # Fetch activities per issue
    for iid in all_issues:
        activities = yt_get(
            f"/api/issues/{iid}/activities?"
            f"fields=id,timestamp,author(login,name),added(name),removed(name),field(name)"
            f"&categories=CustomFieldCategory&$top=30",
            yt_token,
        )
        all_issues[iid]["_activities"] = activities or []

    return all_issues


# ── Work Item Construction ───────────────────────────────────────────

def build_pr_items(prs, lwd, today):
    """Build work items from GitHub PRs."""
    items = []

    for num, pr in prs.items():
        title = pr.get("title", "")
        branch = pr.get("headRefName", "")
        tickets = extract_tickets(title) or extract_tickets(branch)
        created_et = iso_to_et(pr.get("createdAt"))
        merged_et = iso_to_et(pr.get("mergedAt"))
        state = (pr.get("state") or "").lower()
        commits = pr.get("_commits", [])
        reviews = pr.get("_reviews", [])

        created_date = to_date(created_et)

        # Collect review info
        review_info = []
        for r in reviews:
            author = r.get("author", {})
            login = author.get("login", "") if isinstance(author, dict) else str(author)
            if login == GITHUB_USER:
                continue
            review_date = iso_to_et(r.get("submittedAt"))
            review_info.append({
                "reviewer": login,
                "state": (r.get("state") or "").lower(),
                "date": to_date(review_date).isoformat() if review_date else None,
            })

        # PR opened — attribute to createdAt date
        if created_date and created_date >= lwd:
            items.append({
                "date": created_date.isoformat(),
                "type": "pr_opened",
                "tickets": tickets,
                "pr": num,
                "prTitle": title,
                "prUrl": gh_pr_url(num),
                "prState": state,
                "mergedOn": to_date(merged_et).isoformat() if merged_et else None,
                "reviews": review_info,
            })

        # PR feedback addressed — commits on later days after reviews
        if commits and created_date:
            # Find earliest review date
            review_dates = [
                to_date(iso_to_et(r.get("submittedAt")))
                for r in reviews
                if iso_to_et(r.get("submittedAt"))
            ]
            earliest_review = min(review_dates) if review_dates else None

            feedback_dates_seen = set()
            for commit in commits:
                commit_et = iso_to_et(commit.get("committedDate"))
                commit_date = to_date(commit_et)
                if not commit_date or commit_date < lwd:
                    continue
                # Must be after PR creation AND after a review
                if commit_date <= created_date:
                    continue
                if not earliest_review or commit_date <= earliest_review:
                    continue
                if commit_date in feedback_dates_seen:
                    continue
                feedback_dates_seen.add(commit_date)
                items.append({
                    "date": commit_date.isoformat(),
                    "type": "pr_feedback_addressed",
                    "tickets": tickets,
                    "pr": num,
                    "prTitle": title,
                    "prUrl": gh_pr_url(num),
                })

        # PR opened before window but still active — include as context for today
        if created_date and created_date < lwd and state == "open":
            items.append({
                "date": today.isoformat(),
                "type": "pr_in_review",
                "tickets": tickets,
                "pr": num,
                "prTitle": title,
                "prUrl": gh_pr_url(num),
                "reviews": review_info,
            })

    return items


def build_youtrack_items(issues, lwd, today):
    """Build work items from YouTrack issues and activities."""
    items = []

    for iid, issue in issues.items():
        summary = issue.get("summary", "")
        stage = extract_yt_field(issue, "Stage")
        activities = issue.get("_activities", [])

        # Stage changes by Eli in the window
        for act in activities:
            author = act.get("author", {})
            login = author.get("login", "") if isinstance(author, dict) else ""
            if login != YOUTRACK_LOGIN:
                continue

            ts = ms_to_et(act.get("timestamp"))
            act_date = to_date(ts)
            if not act_date or act_date < lwd:
                continue

            field_name = (act.get("field") or {}).get("name", "")
            # Only Stage changes are standup-worthy (not Assignee, Carrier, etc.)
            if field_name != "Stage":
                continue

            added_names = activity_value_names(act.get("added"))
            removed_names = activity_value_names(act.get("removed"))

            if not added_names:
                continue

            items.append({
                "date": act_date.isoformat(),
                "type": "stage_change",
                "ticket": iid,
                "ticketSummary": summary,
                "ticketUrl": yt_url(iid),
                "from": removed_names[0] if removed_names else None,
                "to": added_names[0],
            })

        # Active tickets → today
        if stage in ("Develop", "Review"):
            items.append({
                "date": today.isoformat(),
                "type": "active_ticket",
                "ticket": iid,
                "ticketSummary": summary,
                "ticketUrl": yt_url(iid),
                "stage": stage,
            })

    return items


# ── Main ─────────────────────────────────────────────────────────────

def main():
    now_et = to_et(datetime.now(timezone.utc))
    today = now_et.date()
    lwd = last_working_day(today)

    yt_token = get_youtrack_token()

    # Gather data
    prs = gather_github_prs(lwd)
    issues = gather_youtrack(yt_token, lwd, today)

    # Build work items
    items = []
    items.extend(build_pr_items(prs, lwd, today))
    items.extend(build_youtrack_items(issues, lwd, today))

    # Build ticket details lookup (for tickets referenced by PRs)
    ticket_details = {}
    for iid, issue in issues.items():
        ticket_details[iid] = {
            "summary": issue.get("summary", ""),
            "url": yt_url(iid),
            "stage": extract_yt_field(issue, "Stage"),
        }

    # Sort: by date, then type priority
    type_order = {
        "pr_opened": 0,
        "pr_feedback_addressed": 1,
        "stage_change": 2,
        "active_ticket": 3,
        "pr_in_review": 4,
    }
    items.sort(key=lambda x: (x["date"], type_order.get(x["type"], 99)))

    # Output
    output = {
        "dates": {
            "today": today.isoformat(),
            "todayName": calendar.day_name[today.weekday()],
            "lastWorkingDay": lwd.isoformat(),
            "lastWorkingDayName": calendar.day_name[lwd.weekday()],
        },
        "ticketDetails": ticket_details,
        "workItems": items,
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
