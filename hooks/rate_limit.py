#!/usr/bin/env python3
"""Shared 5-hour usage-window gate for the PreToolUse and UserPromptSubmit hooks.

Neither hook's payload carries rate_limits; the statusline payload does, so
statusline.ps1 writes each reading to RATE_LIMIT_STATE and both hooks read it here.
That reading is a snapshot, and usage only climbs inside a window, so it can only
under-report: the cutoff fires late rather than locking anyone out early.

Both hooks import this module so the threshold is defined once.
"""

import json
import os
import time

RATE_LIMIT_STATE = os.path.expanduser("~/.claude/rate-limit-state.json")
RATE_LIMIT_BLOCK_PERCENTAGE = 95
RATE_LIMIT_STALE_SECONDS = 20 * 60

ESCAPE_HATCH = (
    "To keep working now, set CLAUDE_IGNORE_RATE_LIMIT=1 in the env block of "
    "~/.claude/settings.json and restart the session. Do NOT delete or edit "
    "~/.claude/rate-limit-state.json to get around this, and do not raise "
    "RATE_LIMIT_BLOCK_PERCENTAGE. STOP and tell the user."
)


def window_exhausted():
    """Return (used_percentage, minutes_to_reset) when the window is spent, else None."""
    if os.environ.get("CLAUDE_IGNORE_RATE_LIMIT"):
        return None

    try:
        with open(RATE_LIMIT_STATE, encoding="utf-8-sig") as fh:
            state = json.load(fh)
    except Exception:
        return None

    used = state.get("five_hour_used_percentage")
    if not isinstance(used, (int, float)) or used < RATE_LIMIT_BLOCK_PERCENTAGE:
        return None

    now = int(time.time())

    # A reading from before the window rolled over says nothing about the window we are in.
    resets_at = state.get("resets_at")
    if isinstance(resets_at, (int, float)) and now >= resets_at:
        return None

    # The statusline rewrites this on every render, so a long gap means it has not run
    # and the percentage may have moved.
    captured_at = state.get("captured_at")
    if isinstance(captured_at, (int, float)) and now - captured_at > RATE_LIMIT_STALE_SECONDS:
        return None

    minutes = None
    if isinstance(resets_at, (int, float)):
        minutes = max(0, int((resets_at - now) / 60))

    return int(used), minutes


def block_message(what_is_stopped):
    """The stderr text for a blocked call, or None when the window still has room."""
    spent = window_exhausted()
    if spent is None:
        return None

    used, minutes = spent
    reset_note = "" if minutes is None else " The window resets in {} minute(s).".format(minutes)

    return (
        "BLOCKED: the 5-hour usage window is at {}%, at or past the {}% cutoff.{}\n"
        "{} Nothing is wrong with the request itself.\n"
        "{}".format(used, RATE_LIMIT_BLOCK_PERCENTAGE, reset_note, what_is_stopped, ESCAPE_HATCH)
    )
