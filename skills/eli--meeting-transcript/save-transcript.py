"""Save a Teams meeting transcript that the Microsoft 365 connector already returned in this session.

The connector returns the transcript inline as a tool result, so there is no file to copy. Claude Code
logs every tool result to the session's JSONL under ~/.claude/projects/. This script finds the
read_resource call whose uri matches --uri, takes its result from that log, and writes it to disk.
That keeps the transcript byte-for-byte as Microsoft returned it, with nothing retyped by the agent.

Usage:
    python save-transcript.py --uri "<meeting-transcript:///...>" [--ticket-folder SW-XXXXX-title]

Output lands in:
    ~/.claude/tickets/<ticket-folder>/artifacts/meetings/<date>-<subject>/   (with --ticket-folder)
    ~/.claude/meetings/<date>-<subject>/                                      (without)

Prints a JSON summary to stdout. Exits non-zero when the call can't be found or holds no transcript.
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

CLAUDE_HOME = os.path.join(os.path.expanduser("~"), ".claude")
PROJECTS_DIR = os.path.join(CLAUDE_HOME, "projects")
READ_RESOURCE_TOOL_SUFFIX = "Microsoft_365__read_resource"
SESSION_LOGS_TO_SEARCH = 20
CUE_TIMING = re.compile(r"^(\d{2}:\d{2}:\d{2})\.\d{3}\s+-->\s+")
VOICE_TAG = re.compile(r"<v\s+([^>]*)>(.*?)(?:</v>)?$", re.DOTALL)


def fail(message):
    print(json.dumps({"error": message}, indent=2))
    sys.exit(1)


def find_tool_result(uri):
    """Return (result_text, is_error, log_path) for the most recent read_resource call on uri."""
    logs = glob.glob(os.path.join(PROJECTS_DIR, "**", "*.jsonl"), recursive=True)
    logs.sort(key=os.path.getmtime, reverse=True)
    for log_path in logs[:SESSION_LOGS_TO_SEARCH]:
        matching_tool_use_ids = set()
        latest_result = None
        with open(log_path, encoding="utf-8") as log:
            for line in log:
                if uri not in line and not matching_tool_use_ids:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                content = (record.get("message") or {}).get("content")
                if not isinstance(content, list):
                    continue
                for block in content:
                    if (block.get("type") == "tool_use"
                            and block.get("name", "").endswith(READ_RESOURCE_TOOL_SUFFIX)
                            and (block.get("input") or {}).get("uri") == uri):
                        matching_tool_use_ids.add(block["id"])
                    elif block.get("type") == "tool_result" and block.get("tool_use_id") in matching_tool_use_ids:
                        result = block.get("content")
                        if isinstance(result, list):
                            result = "".join(part.get("text", "") for part in result if part.get("type") == "text")
                        latest_result = (result or "", bool(block.get("is_error")), log_path)
        if latest_result:
            return latest_result
    return None


def occurrence_local_date(uri, transcript):
    """The meeting date in local time: the occurrence start from the uri, else the transcript's creation time."""
    start_values = parse_qs(urlparse(uri).query).get("start")
    stamp = start_values[0] if start_values else transcript.get("createdDateTime", "")
    try:
        moment = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return "unknown-date"
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone().strftime("%Y-%m-%d")


def slugify(text):
    slug = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return slug or "meeting"


def parse_cues(vtt):
    """Yield (start, speaker, text) for each cue. Speaker is '' when the cue has no voice tag."""
    lines = vtt.replace("\r\n", "\n").split("\n")
    index = 0
    while index < len(lines):
        timing = CUE_TIMING.match(lines[index])
        index += 1
        if not timing:
            continue
        payload = []
        while index < len(lines) and lines[index].strip():
            payload.append(lines[index].strip())
            index += 1
        body = " ".join(payload)
        voice = VOICE_TAG.match(body)
        if voice:
            yield timing.group(1), voice.group(1).strip(), voice.group(2).strip()
        elif body:
            yield timing.group(1), "", body


def to_compact_markdown(subject, date, transcript):
    """One paragraph per speaker turn: consecutive cues from the same speaker are joined."""
    turns = []
    for start, speaker, text in parse_cues(transcript.get("content", "")):
        if turns and turns[-1][1] == speaker:
            turns[-1][2].append(text)
        else:
            turns.append((start, speaker, [text]))
    header = [
        f"# {subject} ({date})",
        "",
        f"Transcript {transcript.get('createdDateTime', '?')} to {transcript.get('endDateTime', '?')} (UTC).",
        "Times are offsets into the transcript. Speaker labels are Teams' attribution and can be wrong.",
    ]
    body = [f"[{start}] **{speaker or 'Unattributed'}:** {' '.join(texts)}" for start, speaker, texts in turns]
    speaker_turns = {}
    for _, speaker, _ in turns:
        speaker_turns[speaker or "Unattributed"] = speaker_turns.get(speaker or "Unattributed", 0) + 1
    return "\n\n".join(["\n".join(header)] + body) + "\n", speaker_turns


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--uri", required=True, help="The meeting-transcript:/// uri passed to read_resource, verbatim")
    parser.add_argument("--ticket-folder", help="Ticket folder name under ~/.claude/tickets/")
    args = parser.parse_args()

    if not args.uri.startswith("meeting-transcript:///"):
        fail("--uri must be the meeting-transcript:/// uri from the calendar event's meetingTranscriptUrl")

    found = find_tool_result(args.uri)
    if not found:
        fail(f"No read_resource call on this uri in the {SESSION_LOGS_TO_SEARCH} most recent session logs. "
             "Call read_resource on the uri first, then rerun with the identical string.")
    result_text, is_error, log_path = found
    if is_error:
        fail(f"The read_resource call failed: {result_text}")
    try:
        result = json.loads(result_text)
    except json.JSONDecodeError:
        fail(f"The read_resource result is not JSON: {result_text[:500]}")

    transcripts = [t for t in result.get("transcripts") or [] if t.get("content")]
    if not transcripts:
        fail("The read_resource result holds no transcript content. "
             f"Result: {json.dumps(result)[:500]}")

    subject = (result.get("meeting") or {}).get("subject") or "meeting"
    date = occurrence_local_date(args.uri, transcripts[0])
    if args.ticket_folder:
        base_dir = os.path.join(CLAUDE_HOME, "tickets", args.ticket_folder, "artifacts", "meetings")
    else:
        base_dir = os.path.join(CLAUDE_HOME, "meetings")
    out_dir = os.path.join(base_dir, f"{date}-{slugify(subject)}")
    os.makedirs(out_dir, exist_ok=True)

    files = []
    for number, transcript in enumerate(transcripts, start=1):
        suffix = "" if len(transcripts) == 1 else f"-{number}"
        vtt_path = os.path.join(out_dir, f"transcript{suffix}.vtt")
        md_path = os.path.join(out_dir, f"transcript{suffix}.md")
        with open(vtt_path, "w", encoding="utf-8", newline="") as vtt_file:
            vtt_file.write(transcript["content"])
        markdown, speaker_turns = to_compact_markdown(subject, date, transcript)
        with open(md_path, "w", encoding="utf-8") as md_file:
            md_file.write(markdown)
        files.append({
            "vtt": vtt_path,
            "markdown": md_path,
            "createdDateTime": transcript.get("createdDateTime"),
            "endDateTime": transcript.get("endDateTime"),
            "speakerTurns": speaker_turns,
        })

    with open(os.path.join(out_dir, "source.json"), "w", encoding="utf-8") as source_file:
        json.dump({"subject": subject, "uri": args.uri, "sessionLog": log_path}, source_file, indent=2)

    print(json.dumps({"subject": subject, "date": date, "outDir": out_dir, "transcripts": files}, indent=2))


if __name__ == "__main__":
    main()
