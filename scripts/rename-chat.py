#!/usr/bin/env python3
"""Rename the current Claude Code chat.

Appends a custom-title entry, the same entry /rename writes, to the chat's transcript.
The running app re-reads its title from the transcript.

Usage: python rename-chat.py "<title>"
"""

import glob
import json
import os
import sys


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        print('Usage: python rename-chat.py "<title>"', file=sys.stderr)
        sys.exit(1)
    title = sys.argv[1].strip()

    session_id = os.environ.get("CLAUDE_CODE_SESSION_ID")
    if not session_id:
        print("ERROR: CLAUDE_CODE_SESSION_ID is not set; run this from inside a Claude Code chat.", file=sys.stderr)
        sys.exit(1)

    transcript_paths = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{session_id}.jsonl"))
    if len(transcript_paths) != 1:
        print(f"ERROR: expected one transcript for chat {session_id}, found {len(transcript_paths)}.", file=sys.stderr)
        sys.exit(1)

    custom_title_entry = {"type": "custom-title", "customTitle": title, "sessionId": session_id}
    # Compact separators: the running app finds the entry by the literal text "type":"custom-title".
    compact_json_separators = (",", ":")
    with open(transcript_paths[0], "a", encoding="utf-8") as transcript:
        transcript.write(json.dumps(custom_title_entry, ensure_ascii=False, separators=compact_json_separators) + "\n")
    print(f"Renamed chat to: {title}")


if __name__ == "__main__":
    main()
