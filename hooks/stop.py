#!/usr/bin/env python3
"""Stop hook: audit the assistant's last turn for rule violations.

Fires when the assistant finishes its turn. Scans the most recent assistant text
output for red-flag phrases that often appear when the assistant takes action on a
question without authorization (Gate 1 violation). Non-blocking — surfaces warnings
visibly in the transcript so Eli sees patterns in real time instead of after the fact.
"""

import json
import os
import re
import sys

# (regex, human-readable warning)
RED_FLAG_PATTERNS = [
    (
        r"\b(updating|applying|editing) (the )?plan now\b",
        "Possible Gate 1 violation: 'updating the plan now' phrasing often appears "
        "when the user asked a question, not when they authorized an action.",
    ),
    (
        r"\bI'?ll (fix|apply|update|add|remove|change|implement|edit|create|draft|post|send)\b",
        "Possible Gate 1 violation: 'I'll do X' announces action — verify the user used "
        "an imperative or explicit authorization in their last message.",
    ),
    (
        r"\b(going|about) to (apply|update|edit|fix|implement|post|send|create)\b",
        "Possible Gate 1 violation: 'going to do X' phrasing often appears without "
        "imperative authorization.",
    ),
    (
        r"\blet me (apply|update|fix|edit|implement|draft|post|send|create)\b",
        "Possible Gate 1 violation: 'let me X' often precedes an action without "
        "explicit authorization.",
    ),
    (
        r"\bproceeding (with|to)\b",
        "Possible Gate 1 violation: 'proceeding with' implies action — verify "
        "authorization, not just acknowledgement.",
    ),
]


TICKET_NUMBER_RE = re.compile(r"(?<![\w/-])SW-\d{4,6}(?![\w/-])")
QUOTED_TITLE_RE = re.compile(r'\s*["“][^"”\n]+["”]')
TICKET_NUMBER_RULE_PATTERN = r"^## Ticket numbers:.*?(?=^## |\Z)"


def ticket_number_rule():
    """The talking-to-eli.md section the block enforces, so the rule text lives in one place."""
    rules_path = os.path.expanduser("~/.claude/rules/talking-to-eli.md")
    try:
        with open(rules_path, encoding="utf-8-sig") as rules_file:
            match = re.search(TICKET_NUMBER_RULE_PATTERN, rules_file.read(), re.S | re.M)
    except OSError:
        return ""
    return match.group(0).strip() if match else ""


def strip_exempt_regions(text):
    """Code, quoted drafts of posted text and links may carry bare ticket numbers."""
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"^\s*>.*$", " ", text, flags=re.MULTILINE)
    text = re.sub(r"`[^`\n]*`", " ", text)
    return re.sub(r"https?://\S+", " ", text)


def find_untitled_tickets(text):
    """Ticket numbers not followed by a quoted title, in order of first appearance."""
    checked_text = strip_exempt_regions(text)
    untitled = []
    for match in TICKET_NUMBER_RE.finditer(checked_text):
        if not QUOTED_TITLE_RE.match(checked_text, match.end()) and match.group() not in untitled:
            untitled.append(match.group())
    return untitled


def extract_last_assistant_text(transcript_path):
    """Return the concatenated text content of the most recent assistant turn."""
    last_text = []
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                role = entry.get("role") or entry.get("type") or ""
                if role not in ("assistant", "model"):
                    # Reset if we see a non-assistant message — we want only the LAST contiguous assistant turn.
                    if last_text and role in ("user", "human"):
                        last_text = []
                    continue
                content = entry.get("content")
                if content is None:
                    msg = entry.get("message", {})
                    content = msg.get("content") if isinstance(msg, dict) else None
                if isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            text = part.get("text", "")
                            if text:
                                last_text.append(text)
                elif isinstance(content, str) and content:
                    last_text.append(content)
    except FileNotFoundError:
        return ""
    except Exception:
        return ""
    return "\n".join(last_text)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    text = data.get("last_assistant_message") or ""
    if not text:
        transcript_path = data.get("transcript_path") or data.get("transcriptPath", "")
        if transcript_path:
            text = extract_last_assistant_text(transcript_path)
    if not text:
        sys.exit(0)

    untitled = find_untitled_tickets(text)

    warnings = []
    seen = set()
    for pattern, msg in RED_FLAG_PATTERNS:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        if matches and msg not in seen:
            warnings.append(f"  - {msg}")
            seen.add(msg)

    output = {}
    if warnings:
        body = "\n".join(warnings)
        # Surface via systemMessage so it appears in the UI.
        output["systemMessage"] = (
            "=== STOP HOOK AUDIT — possible rule violation(s) in last turn ===\n"
            + body
            + "\n=== END AUDIT ==="
        )
    if untitled:
        output["decision"] = "block"
        output["reason"] = (
            "Ticket numbers without their YouTrack title: "
            + ", ".join(untitled)
            + ". Rewrite the message to follow talking-to-eli.md § Ticket numbers:\n\n"
            + ticket_number_rule()
        )
    if output:
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
