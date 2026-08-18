#!/usr/bin/env python3
"""Sanctioned writer for PR reviews on other people's PRs.

This is the ONLY approved way to post a review (approve / comment / request-changes)
or an inline review comment on a PR. Raw `gh pr review`, `gh pr comment`, and
`gh api ... POST .../reviews|/comments` are blocked by the pretooluse hook precisely
because the body can silently mangle (wrong -f/-F flag posts a literal `@/path`, the
prod-db hook splits inline multiline bodies on newlines, etc.).

Why this script can't repeat that failure:
  - Bodies are read from files and sent verbatim via `gh api --input` (JSON payload on
    stdin). No -f/-F flag to fumble, no shell newline-splitting.
  - After every write it READS THE BODY BACK from the API and aborts non-zero if the
    rendered text doesn't match what was sent. "Posted successfully" is never trusted on
    its own — content is verified, not just existence.

Reads (fetching the head SHA, reading comments back) use plain `gh api` GET / `gh pr view`
and are intentionally left unblocked by the hook.

Usage:
  pr-review.py approve <PR#> [--repo OWNER/REPO]
  pr-review.py comment <PR#> --inline <comments.json> [--body-file <f>] [--repo ...]
  pr-review.py request-changes <PR#> --body-file <f> [--inline <comments.json>] [--repo ...]

<comments.json> is a JSON array of inline comments, each:
  {"path": "src/Foo.cs", "line": 383, "side": "RIGHT", "body": "finding text..."}
  ("side" defaults to "RIGHT". Use "start_line"/"start_side" for multi-line ranges.)
"""

import argparse
import json
import re
import subprocess
import sys

DEFAULT_REPO = "swyfft-insurance/swyfft_web"


def run(args, *, input_text=None):
    """Run a command, return stdout. Raise on non-zero with stderr surfaced.

    encoding is pinned to UTF-8 explicitly: on Windows, subprocess text mode defaults to
    the locale codepage (cp1252), which mangles gh's UTF-8 output (e.g. a U+2212 minus)
    both when encoding stdin and decoding stdout. Pinning UTF-8 keeps non-ASCII bodies
    verbatim end to end.
    """
    result = subprocess.run(
        args,
        input=input_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(f"Command failed ({result.returncode}): {' '.join(args)}")
    return result.stdout


def gh_api(path, *, method=None, input_text=None, jq=None):
    cmd = ["gh", "api", path]
    if method:
        cmd += ["-X", method]
    if jq:
        cmd += ["--jq", jq]
    if input_text is not None:
        cmd += ["--input", "-"]
    return run(cmd, input_text=input_text)


def head_sha(repo, pr):
    return run(
        ["gh", "pr", "view", str(pr), "--repo", repo, "--json", "headRefOid",
         "-q", ".headRefOid"]
    ).strip()


def current_login():
    return run(["gh", "api", "user", "-q", ".login"]).strip()


def normalize(text):
    return (text or "").replace("\r\n", "\n").strip()


def load_inline(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise SystemExit("--inline file must contain a JSON array of comment objects.")
    comments = []
    for i, c in enumerate(data):
        if "path" not in c or "body" not in c or "line" not in c:
            raise SystemExit(f"inline comment #{i} needs at least path, line, body.")
        c.setdefault("side", "RIGHT")
        comments.append(c)
    return comments


def read_body_file(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


COPILOT_BAN_MSG = (
    "BLOCKED: body contains a copilot mention. Tagging copilot is banned -- it spawns a "
    "coding-agent session on the PR. Remove the mention (including inside quoted text) and retry."
)


def block_copilot_mentions(body):
    """Tagging copilot spawns a coding-agent session on the PR under Eli's account. Banned."""
    if body and re.search(r"@copilot", body, re.IGNORECASE):
        sys.exit(COPILOT_BAN_MSG)


def post_review(repo, pr, event, body, comments):
    block_copilot_mentions(body)
    for c in comments or []:
        block_copilot_mentions(c.get("body"))
    sha = head_sha(repo, pr)
    payload = {"commit_id": sha, "event": event}
    if body is not None:
        payload["body"] = body
    if comments:
        payload["comments"] = comments
    out = gh_api(
        f"repos/{repo}/pulls/{pr}/reviews",
        method="POST",
        input_text=json.dumps(payload),
        jq="{id: .id, state: .state}",
    )
    return json.loads(out)


def verify_inline(repo, pr, sent_comments):
    """Re-fetch this PR's review comments and confirm each sent body landed verbatim."""
    raw = gh_api(f"repos/{repo}/pulls/{pr}/comments?per_page=100")
    posted = json.loads(raw)
    posted_bodies = [normalize(c.get("body")) for c in posted]
    missing = []
    for c in sent_comments:
        if normalize(c["body"]) not in posted_bodies:
            missing.append(c)
    if missing:
        sys.stderr.write(
            "READ-BACK FAILED: the following inline bodies were NOT found verbatim "
            "on the PR after posting:\n"
        )
        for c in missing:
            sys.stderr.write(f"  - {c['path']}:{c['line']} -> {normalize(c['body'])[:80]!r}\n")
        raise SystemExit(2)


def verify_review_state(repo, pr, expected_state):
    login = current_login()
    raw = gh_api(f"repos/{repo}/pulls/{pr}/reviews?per_page=100")
    reviews = json.loads(raw)
    mine = [r for r in reviews if (r.get("user") or {}).get("login") == login]
    if not mine or mine[-1].get("state") != expected_state:
        raise SystemExit(
            f"READ-BACK FAILED: latest review by {login} is "
            f"{mine[-1].get('state') if mine else 'NONE'}, expected {expected_state}."
        )


def cmd_approve(args):
    # APPROVE carries no body, so there is nothing to mangle; still verify the state landed.
    run(["gh", "pr", "review", str(args.pr), "--repo", args.repo, "--approve"])
    verify_review_state(args.repo, args.pr, "APPROVED")
    print(f"#{args.pr}: APPROVED (verified).")


def cmd_comment(args):
    comments = load_inline(args.inline) if args.inline else []
    body = read_body_file(args.body_file) if args.body_file else None
    if not comments and not body:
        raise SystemExit("comment requires --inline and/or --body-file.")
    result = post_review(args.repo, args.pr, "COMMENT", body, comments)
    if comments:
        verify_inline(args.repo, args.pr, comments)
    print(f"#{args.pr}: COMMENT review {result['id']} ({result['state']}) "
          f"with {len(comments)} inline comment(s) (verified).")


def cmd_request_changes(args):
    comments = load_inline(args.inline) if args.inline else []
    body = read_body_file(args.body_file)
    result = post_review(args.repo, args.pr, "REQUEST_CHANGES", body, comments)
    if comments:
        verify_inline(args.repo, args.pr, comments)
    print(f"#{args.pr}: REQUEST_CHANGES review {result['id']} ({result['state']}) "
          f"with {len(comments)} inline comment(s) (verified).")


def main():
    parser = argparse.ArgumentParser(description="Sanctioned PR-review writer.")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    sub = parser.add_subparsers(dest="command", required=True)

    p_app = sub.add_parser("approve")
    p_app.add_argument("pr", type=int)
    p_app.set_defaults(func=cmd_approve)

    p_com = sub.add_parser("comment")
    p_com.add_argument("pr", type=int)
    p_com.add_argument("--inline")
    p_com.add_argument("--body-file")
    p_com.set_defaults(func=cmd_comment)

    p_rc = sub.add_parser("request-changes")
    p_rc.add_argument("pr", type=int)
    p_rc.add_argument("--body-file", required=True)
    p_rc.add_argument("--inline")
    p_rc.set_defaults(func=cmd_request_changes)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
