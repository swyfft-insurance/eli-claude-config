"""YouTrack batch actions: validate, render canonically, stage, and execute.

One approval covers a whole batch because the approval is bound to exact content:
pretooluse.py re-renders the staged batch with THIS module and requires that rendering,
verbatim, in the assistant message the user approved. Rendering and validation live only
here so the gate and the executor can never disagree.

Flow:
  stage   -> validate a batch JSON, freeze it under staged/<hash>.json, print the
             canonical block (the assistant pastes it verbatim into chat for approval).
  execute -> run the staged actions against YouTrack, then move the file to executed/
             (single-use; a retry requires a fresh stage and a fresh approval).

Batch JSON shape:
  {"actions": [
      {"type": "comment",         "issue": "SW-1", "text": "..."},
      {"type": "link",            "issue": "SW-1", "linkType": "duplicates", "target": "SW-2"},
      {"type": "setStage",        "issue": "SW-1", "value": "Done"},
      {"type": "setReleaseStage", "issue": "SW-1", "value": "NA"},
      {"type": "setAssignee",     "issue": "SW-1", "value": "eli.koslofsky"},
      {"type": "addFields",       "issue": "SW-1",
       "fields": {"Carrier": ["QBE"], "USState": ["NC", "NY"]}}
  ]}
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

BATCH_DIR = os.path.expanduser("~/.claude/youtrack-batches")
STAGED_DIR = os.path.join(BATCH_DIR, "staged")
EXECUTED_DIR = os.path.join(BATCH_DIR, "executed")
YOUTRACK_BASE = "https://swyfft.myjetbrains.com/youtrack"

MAX_ACTIONS = 12
MAX_COMMENT_CHARS = 8000
HASH_CHARS = 12
ISSUE_RE = re.compile(r"^SW-\d+$")

# Closed value sets: every settable value is enumerated, so a batch can never smuggle
# extra command tokens into the YouTrack command API.
STAGE_VALUES = [
    "Backlog", "Ready for Dev", "Develop", "Review",
    "Ready for Test", "Test", "Failed Test", "Tested", "Done",
]
RELEASE_STAGE_VALUES = ["NA", "Development", "Beta", "Production"]
# The only assignee a batch may set. Assigning anyone else is a single action, not a batch.
ASSIGNEE_VALUES = ["eli.koslofsky"]
LINK_TYPES = [
    "duplicates", "relates to", "subtask of",
    "depends on", "is duplicated by", "parent for",
]
# Scoping fields an action may write, with every permitted value enumerated. The command
# API takes a free-text query, so an unenumerated value would be a token-injection hole.
FIELD_VALUES = {
    "ProductLine": [
        "Commercial", "HO", "Flood", "GRC",
        "Deductible Buyback HO", "DP3", "Deductible Buyback CO",
    ],
    "Carrier": [
        "Clear Blue", "Clear Blue Specialty", "Benchmark", "Vave", "Core Specialty",
        "Topa", "Granada", "Hiscox", "NFIP", "TMK", "Brit", "Dorchester",
        "Benchmark Specialty", "Emerald Bay", "Ark", "QBE", "Hadron",
    ],
    "RatingType": ["Admitted", "E&S"],
    "USState": [
        "AL", "MA", "TX", "NY", "NJ", "FL", "IL", "CA",
        "LA", "NC", "WA", "SC", "VA", "OK", "MS", "GA",
    ],
}
ACTION_TYPES = ["comment", "link", "setStage", "setReleaseStage", "setAssignee", "addFields"]


def canonical_json(actions):
    return json.dumps(actions, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def batch_hash(actions):
    return hashlib.sha256(canonical_json(actions).encode("utf-8")).hexdigest()[:HASH_CHARS]


def validate(batch):
    """Return a list of error strings; empty list means the batch is valid."""
    errors = []
    if not isinstance(batch, dict) or not isinstance(batch.get("actions"), list):
        return ['batch must be an object with an "actions" array']
    actions = batch["actions"]
    if not actions:
        errors.append("batch has no actions")
    if len(actions) > MAX_ACTIONS:
        errors.append(f"batch has {len(actions)} actions; max is {MAX_ACTIONS}")
    for i, a in enumerate(actions, 1):
        where = f"action {i}"
        if not isinstance(a, dict):
            errors.append(f"{where}: not an object")
            continue
        atype = a.get("type")
        if atype not in ACTION_TYPES:
            errors.append(f"{where}: type {atype!r} not in {ACTION_TYPES}")
            continue
        issue = a.get("issue", "")
        if not ISSUE_RE.match(str(issue)):
            errors.append(f"{where}: issue {issue!r} does not match SW-<digits>")
        allowed_keys = {
            "comment": {"type", "issue", "text"},
            "link": {"type", "issue", "linkType", "target"},
            "setStage": {"type", "issue", "value"},
            "setReleaseStage": {"type", "issue", "value"},
            "setAssignee": {"type", "issue", "value"},
            "addFields": {"type", "issue", "fields"},
        }[atype]
        extra = set(a.keys()) - allowed_keys
        if extra:
            errors.append(f"{where}: unexpected keys {sorted(extra)}")
        if atype == "comment":
            text = a.get("text")
            if not isinstance(text, str) or not text.strip():
                errors.append(f"{where}: comment text is empty")
            elif len(text) > MAX_COMMENT_CHARS:
                errors.append(f"{where}: comment text is {len(text)} chars; max {MAX_COMMENT_CHARS}")
        elif atype == "link":
            if a.get("linkType") not in LINK_TYPES:
                errors.append(f"{where}: linkType {a.get('linkType')!r} not in {LINK_TYPES}")
            if not ISSUE_RE.match(str(a.get("target", ""))):
                errors.append(f"{where}: target {a.get('target')!r} does not match SW-<digits>")
        elif atype == "setStage":
            if a.get("value") not in STAGE_VALUES:
                errors.append(f"{where}: Stage value {a.get('value')!r} not in {STAGE_VALUES}")
        elif atype == "setReleaseStage":
            if a.get("value") not in RELEASE_STAGE_VALUES:
                errors.append(
                    f"{where}: Release Stage value {a.get('value')!r} not in {RELEASE_STAGE_VALUES}")
        elif atype == "setAssignee":
            if a.get("value") not in ASSIGNEE_VALUES:
                errors.append(f"{where}: Assignee value {a.get('value')!r} not in {ASSIGNEE_VALUES}")
        elif atype == "addFields":
            errors.extend(_validate_fields(a.get("fields"), where))
    return errors


def _validate_fields(fields, where):
    """Every field name and every value comes from FIELD_VALUES, so the command query the
    executor builds can only ever contain enumerated tokens."""
    if not isinstance(fields, dict) or not fields:
        return [f"{where}: fields must be a non-empty object"]
    errors = []
    for name, values in fields.items():
        if name not in FIELD_VALUES:
            errors.append(f"{where}: field {name!r} not in {sorted(FIELD_VALUES)}")
            continue
        if not isinstance(values, list) or not values:
            errors.append(f"{where}: {name} must be a non-empty array")
            continue
        if len(set(values)) != len(values):
            errors.append(f"{where}: {name} repeats a value")
        for v in values:
            if v not in FIELD_VALUES[name]:
                errors.append(f"{where}: {name} value {v!r} not in {FIELD_VALUES[name]}")
    return errors


def render(actions):
    """Canonical human-readable rendering. This exact text must appear in the assistant
    message the user approved; pretooluse.py enforces the match."""
    h = batch_hash(actions)
    lines = [f"=== YOUTRACK BATCH {h} ==="]
    for i, a in enumerate(actions, 1):
        if a["type"] == "comment":
            lines.append(f"{i}. {a['issue']}: add comment:")
            lines.append(a["text"])
            lines.append("---")
        elif a["type"] == "link":
            lines.append(f"{i}. {a['issue']}: link \"{a['linkType']}\" {a['target']}")
        elif a["type"] == "setStage":
            lines.append(f"{i}. {a['issue']}: set Stage = {a['value']}")
        elif a["type"] == "setReleaseStage":
            lines.append(f"{i}. {a['issue']}: set Release Stage = {a['value']}")
        elif a["type"] == "setAssignee":
            lines.append(f"{i}. {a['issue']}: set Assignee = {a['value']}")
        elif a["type"] == "addFields":
            pairs = "; ".join(
                f"{name} = {', '.join(values)}" for name, values in sorted(a["fields"].items()))
            lines.append(f"{i}. {a['issue']}: add {pairs}")
    lines.append(f"=== END BATCH {h} ===")
    return "\n".join(lines)


def load_staged(h):
    """Return (actions, error). Recomputes the hash so a swapped file can't ride an old name."""
    path = os.path.join(STAGED_DIR, f"{h}.json")
    if not os.path.exists(path):
        return None, f"nothing staged under hash {h} (already executed, or never staged)"
    try:
        with open(path, encoding="utf-8-sig") as fh:
            batch = json.load(fh)
    except Exception as ex:
        return None, f"staged file unreadable: {ex}"
    errors = validate(batch)
    if errors:
        return None, "staged file no longer validates: " + "; ".join(errors)
    actions = batch["actions"]
    if batch_hash(actions) != h:
        return None, "staged file content does not match its hash (file was modified after staging)"
    return actions, None


def stage(file_path):
    try:
        with open(file_path, encoding="utf-8-sig") as fh:
            batch = json.load(fh)
    except Exception as ex:
        print(f"ERROR: cannot read batch file: {ex}", file=sys.stderr)
        return 1
    errors = validate(batch)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    actions = batch["actions"]
    h = batch_hash(actions)
    os.makedirs(STAGED_DIR, exist_ok=True)
    with open(os.path.join(STAGED_DIR, f"{h}.json"), "w", encoding="utf-8") as fh:
        json.dump({"actions": actions}, fh, ensure_ascii=False, indent=1)
    print(render(actions))
    print()
    print(f"Staged. Paste the block above VERBATIM in your message, get approval, then run:")
    print(f'  & "$HOME/.claude/scripts/YouTrack-Batch.ps1" -Execute -Hash {h}')
    return 0


def _api(method, url, payload, token):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")


def _run_action(a, token):
    if a["type"] == "addFields":
        # One command per field/value pair. A single query listing two values of the same
        # field parses greedily, and this project has prefix pairs ("Clear Blue" and
        # "Clear Blue Specialty"), so one pair per query removes the ambiguity entirely.
        # The command adds to a multi-value field rather than replacing it, which is what
        # "addFields" says; clearing an existing value is not something a batch can do.
        status = None
        for name, values in sorted(a["fields"].items()):
            for value in values:
                status, body = _api(
                    "POST",
                    f"{YOUTRACK_BASE}/api/commands",
                    {"query": f"{name} {value}", "issues": [{"idReadable": a["issue"]}]},
                    token,
                )
        return status, body
    if a["type"] == "comment":
        return _api(
            "POST",
            f"{YOUTRACK_BASE}/api/issues/{a['issue']}/comments?fields=id",
            {"text": a["text"]},
            token,
        )
    query = {
        "link": lambda: f"{a['linkType']} {a['target']}",
        "setStage": lambda: f"Stage {a['value']}",
        "setReleaseStage": lambda: f"Release Stage {a['value']}",
        "setAssignee": lambda: f"Assignee {a['value']}",
    }[a["type"]]()
    return _api(
        "POST",
        f"{YOUTRACK_BASE}/api/commands",
        {"query": query, "issues": [{"idReadable": a["issue"]}]},
        token,
    )


def execute(h):
    token = os.environ.get("YOUTRACK_API_TOKEN", "")
    if not token:
        print("ERROR: YOUTRACK_API_TOKEN is not set", file=sys.stderr)
        return 1
    actions, err = load_staged(h)
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    results = []
    failed = False
    for i, a in enumerate(actions, 1):
        if failed:
            results.append({"action": i, "status": "skipped (earlier action failed)"})
            continue
        try:
            status, _body = _run_action(a, token)
            results.append({"action": i, "status": f"HTTP {status}"})
            print(f"{i}. {a['type']} {a['issue']}: HTTP {status}")
        except urllib.error.HTTPError as ex:
            body = ex.read().decode("utf-8", "replace")[:500]
            results.append({"action": i, "status": f"FAILED HTTP {ex.code}: {body}"})
            print(f"{i}. {a['type']} {a['issue']}: FAILED HTTP {ex.code}: {body}", file=sys.stderr)
            failed = True
        except Exception as ex:
            results.append({"action": i, "status": f"FAILED: {ex}"})
            print(f"{i}. {a['type']} {a['issue']}: FAILED: {ex}", file=sys.stderr)
            failed = True

    # Single-use: consume the stage even on partial failure, so a retry can't silently
    # re-run the actions that already succeeded (comments are not idempotent). Restage
    # only what remains, and get a fresh approval for it.
    os.makedirs(EXECUTED_DIR, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    with open(os.path.join(EXECUTED_DIR, f"{h}-{stamp}.json"), "w", encoding="utf-8") as fh:
        json.dump({"actions": actions, "results": results}, fh, ensure_ascii=False, indent=1)
    try:
        os.remove(os.path.join(STAGED_DIR, f"{h}.json"))
    except OSError:
        pass

    if failed:
        print("Batch stopped at the first failure; the stage is consumed. "
              "Restage the remaining actions and get a fresh approval.", file=sys.stderr)
        return 1
    print(f"Batch {h} executed; record in {EXECUTED_DIR}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    p_stage = sub.add_parser("stage")
    p_stage.add_argument("--file", required=True)
    p_exec = sub.add_parser("execute")
    p_exec.add_argument("--hash", required=True)
    args = parser.parse_args()
    if args.mode == "stage":
        sys.exit(stage(args.file))
    sys.exit(execute(args.hash))


if __name__ == "__main__":
    main()
