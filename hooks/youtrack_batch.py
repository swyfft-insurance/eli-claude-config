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
      {"type": "create",          "ref": "T1", "summary": "...", "description": "...",
       "singleFields": {"IssueType": "Feature", "Priority": "Major"},
       "fields": {"Carrier": ["QBE"]}, "assignee": "konstantin"},
      {"type": "comment",         "issue": "SW-1", "text": "..."},
      {"type": "link",            "issue": "SW-1", "linkType": "duplicates", "target": "SW-2"},
      {"type": "setStage",        "issue": "SW-1", "value": "Done"},
      {"type": "setReleaseStage", "issue": "SW-1", "value": "NA"},
      {"type": "setAssignee",     "issue": "SW-1", "value": "eli.koslofsky"},
      {"type": "addFields",       "issue": "SW-1",
       "fields": {"Carrier": ["QBE"], "USState": ["NC", "NY"]}},
      {"type": "attach",          "issue": "SW-1", "file": "~/.claude/tickets/SW-1/artifacts/x.txt"},
      {"type": "editComment",     "issue": "SW-1", "commentId": "4-123", "text": "..."}
  ]}

An editComment action names an existing comment by id (/eli--read-ticket returns each comment's
id). Staging fetches the comment's current text into the action, so the approved rendering shows
the old text beside the new one. Execution re-fetches the comment and refuses to overwrite it if
it changed after staging.

An attach action names a file under ~/.claude/tickets/. Staging records the file's size and
SHA-256 in the action, so the approval binds to the file's exact content: a file edited after
staging fails validation and cannot be uploaded.

A create action makes a new SW issue and names it with a ref. Any later action in the same batch
can use "@<ref>" as its issue or link target, and execution substitutes the new issue's id.
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

MAX_ACTIONS = 20
MAX_COMMENT_CHARS = 8000
MAX_SUMMARY_CHARS = 250
MAX_DESCRIPTION_CHARS = 20000
HASH_CHARS = 12
ISSUE_RE = re.compile(r"^SW-\d+$")
CREATE_REF_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]{0,9}$")
PROJECT_SHORT_NAME = "SW"

# Closed value sets: every settable value is enumerated, so a batch can never smuggle
# extra command tokens into the YouTrack command API.
STAGE_VALUES = [
    "Backlog", "Ready for Dev", "Blocked", "Develop", "Review",
    "Ready for Test", "Test", "Failed Test", "Tested", "Done",
]
RELEASE_STAGE_VALUES = ["NA", "Development", "Beta", "Production"]
# Assignees a batch may set, enumerated so a login can never carry extra command tokens.
ASSIGNEE_VALUES = [
    "alex.good", "chris", "chris.schenk", "dan.melson", "darius", "ehren", "eli.koslofsky",
    "eric.chen", "jay", "jill.ashley", "jnichols", "john.deangelis", "justin", "ken",
    "konstantin", "larry.beall", "laurel", "marykay.hurlburt", "phil.hobbs", "ron.ratzlaff",
    "steve.rysavy", "warren.hirschbuehler", "wayne", "wendell",
    "carmen", "drew.house", "james.whitfield", "joshua.spink", "mahendra", "nick.fee",
    "patti.sundius", "surabhi.tiwari",
]
# Single-value fields a create action may set, every value enumerated for the same reason.
SINGLE_FIELD_VALUES = {
    "IssueType": ["Feature", "Bug", "Support", "Epic", "Inquiry"],
    "Priority": ["Minor", "Normal", "Major", "Critical", "Show Stopper"],
    "Platform": ["Internal", "External"],
    "Business Owner": [
        "carmen", "gena.motter", "greg.granger", "jay.prasad", "jennifer.wagner", "ken",
        "roman", "steve.rysavy",
    ],
}
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
ACTION_TYPES = [
    "create", "comment", "link", "setStage", "setReleaseStage", "setAssignee", "addFields",
    "attach", "editComment",
]
COMMENT_ID_RE = re.compile(r"^\d+-\d+$")
# Attachments come only from ticket work folders, so a batch cannot upload an arbitrary file.
ATTACH_ROOT = os.path.normcase(os.path.realpath(os.path.expanduser("~/.claude/tickets")))
MAX_ATTACH_BYTES = 10 * 1024 * 1024


def _attach_path(file_value):
    return os.path.realpath(os.path.expanduser(str(file_value)))


def _file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fingerprint_attachments(actions):
    """Record each attached file's size and hash at stage time. Validation later requires the
    file on disk to still match, so what uploads is exactly what was approved."""
    for a in actions:
        if isinstance(a, dict) and a.get("type") == "attach" and "file" in a:
            path = _attach_path(a["file"])
            a["file"] = path
            if os.path.isfile(path):
                a["bytes"] = os.path.getsize(path)
                a["sha256"] = _file_sha256(path)


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
    refs = set()
    for i, a in enumerate(actions, 1):
        where = f"action {i}"
        if not isinstance(a, dict):
            errors.append(f"{where}: not an object")
            continue
        atype = a.get("type")
        if atype not in ACTION_TYPES:
            errors.append(f"{where}: type {atype!r} not in {ACTION_TYPES}")
            continue
        if atype == "create":
            errors.extend(_validate_create(a, where, refs))
            continue
        issue = a.get("issue", "")
        if not _is_issue_or_known_ref(issue, refs):
            errors.append(f"{where}: issue {issue!r} is neither SW-<digits> nor an earlier create's @ref")
        allowed_keys = {
            "comment": {"type", "issue", "text"},
            "link": {"type", "issue", "linkType", "target"},
            "setStage": {"type", "issue", "value"},
            "setReleaseStage": {"type", "issue", "value"},
            "setAssignee": {"type", "issue", "value"},
            "addFields": {"type", "issue", "fields"},
            "attach": {"type", "issue", "file", "bytes", "sha256"},
            "editComment": {"type", "issue", "commentId", "text", "oldText"},
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
            if not _is_issue_or_known_ref(a.get("target", ""), refs):
                errors.append(
                    f"{where}: target {a.get('target')!r} is neither SW-<digits> nor an earlier create's @ref")
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
        elif atype == "attach":
            errors.extend(_validate_attach(a, where))
        elif atype == "editComment":
            if not COMMENT_ID_RE.match(str(a.get("commentId", ""))):
                errors.append(f"{where}: commentId {a.get('commentId')!r} does not match <digits>-<digits>")
            text = a.get("text")
            if not isinstance(text, str) or not text.strip():
                errors.append(f"{where}: new comment text is empty")
            elif len(text) > MAX_COMMENT_CHARS:
                errors.append(f"{where}: new comment text is {len(text)} chars; max {MAX_COMMENT_CHARS}")
            if not isinstance(a.get("oldText"), str):
                errors.append(f"{where}: current comment text was not fetched at stage time")
            elif a.get("oldText") == text:
                errors.append(f"{where}: new comment text is identical to the current text")
    return errors


def _is_issue_or_known_ref(value, refs):
    value = str(value)
    return bool(ISSUE_RE.match(value)) or (value.startswith("@") and value[1:] in refs)


def _validate_create(a, where, refs):
    errors = []
    allowed_keys = {"type", "ref", "summary", "description", "singleFields", "fields", "assignee"}
    extra = set(a.keys()) - allowed_keys
    if extra:
        errors.append(f"{where}: unexpected keys {sorted(extra)}")
    ref = a.get("ref", "")
    if not CREATE_REF_RE.match(str(ref)):
        errors.append(f"{where}: ref {ref!r} must be a letter followed by up to 9 letters or digits")
    elif ref in refs:
        errors.append(f"{where}: ref {ref!r} is already used by an earlier create")
    else:
        refs.add(ref)
    summary = a.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        errors.append(f"{where}: summary is empty")
    elif "\n" in summary or len(summary) > MAX_SUMMARY_CHARS:
        errors.append(f"{where}: summary must be one line of at most {MAX_SUMMARY_CHARS} chars")
    description = a.get("description", "")
    if not isinstance(description, str):
        errors.append(f"{where}: description must be a string")
    elif len(description) > MAX_DESCRIPTION_CHARS:
        errors.append(f"{where}: description is {len(description)} chars; max {MAX_DESCRIPTION_CHARS}")
    single_fields = a.get("singleFields", {})
    if not isinstance(single_fields, dict):
        errors.append(f"{where}: singleFields must be an object")
    else:
        for name, value in single_fields.items():
            if name not in SINGLE_FIELD_VALUES:
                errors.append(f"{where}: field {name!r} not in {sorted(SINGLE_FIELD_VALUES)}")
            elif value not in SINGLE_FIELD_VALUES[name]:
                errors.append(f"{where}: {name} value {value!r} not in {SINGLE_FIELD_VALUES[name]}")
    if "fields" in a:
        errors.extend(_validate_fields(a["fields"], where))
    if "assignee" in a and a["assignee"] not in ASSIGNEE_VALUES:
        errors.append(f"{where}: Assignee value {a['assignee']!r} not in {ASSIGNEE_VALUES}")
    return errors


def _fetch_comment_text(issue, comment_id, token):
    req = urllib.request.Request(
        f"{YOUTRACK_BASE}/api/issues/{issue}/comments/{comment_id}?fields=id,text",
        method="GET",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8", "replace")).get("text") or ""


def _fetch_old_comment_texts(actions):
    """Freeze each edited comment's current text into its action, so the approval shows exactly
    what is being replaced. Returns a list of error strings."""
    edits = [a for a in actions if isinstance(a, dict) and a.get("type") == "editComment"]
    if not edits:
        return []
    token = os.environ.get("YOUTRACK_API_TOKEN", "")
    if not token:
        return ["YOUTRACK_API_TOKEN is not set; staging an editComment needs it to read the current text"]
    errors = []
    for a in edits:
        a.pop("oldText", None)
        if not ISSUE_RE.match(str(a.get("issue", ""))) or not COMMENT_ID_RE.match(str(a.get("commentId", ""))):
            continue
        try:
            a["oldText"] = _fetch_comment_text(a["issue"], a["commentId"], token)
        except Exception as ex:
            errors.append(f"cannot read comment {a['commentId']} on {a['issue']}: {ex}")
    return errors


def _validate_attach(a, where):
    path = _attach_path(a.get("file", ""))
    if not os.path.normcase(path).startswith(ATTACH_ROOT + os.sep):
        return [f"{where}: attach file {path!r} is not under {ATTACH_ROOT}"]
    if not os.path.isfile(path):
        return [f"{where}: attach file {path!r} does not exist"]
    size = os.path.getsize(path)
    if size == 0:
        return [f"{where}: attach file {path!r} is empty"]
    if size > MAX_ATTACH_BYTES:
        return [f"{where}: attach file is {size} bytes; max {MAX_ATTACH_BYTES}"]
    if a.get("bytes") != size or a.get("sha256") != _file_sha256(path):
        return [f"{where}: attach file {path!r} changed since it was staged"]
    return []


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
        if a["type"] == "create":
            lines.append(f"{i}. create {PROJECT_SHORT_NAME} issue @{a['ref']}:")
            lines.append(f"Summary: {a['summary']}")
            fields = [f"{name} = {value}" for name, value in sorted(a.get("singleFields", {}).items())]
            fields += [f"{name} = {', '.join(values)}" for name, values in sorted(a.get("fields", {}).items())]
            if fields:
                lines.append("Fields: " + "; ".join(fields))
            if a.get("assignee"):
                lines.append(f"Assignee: {a['assignee']}")
            lines.append("Description:")
            lines.append(a.get("description", ""))
            lines.append("---")
        elif a["type"] == "comment":
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
        elif a["type"] == "attach":
            lines.append(
                f"{i}. {a['issue']}: attach {os.path.basename(a['file'])} "
                f"({a['bytes']} bytes, sha256 {a['sha256'][:HASH_CHARS]})")
        elif a["type"] == "editComment":
            lines.append(f"{i}. {a['issue']}: edit comment {a['commentId']}. Current text:")
            lines.append(a["oldText"])
            lines.append("--- replaced with:")
            lines.append(a["text"])
            lines.append("---")
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
    fetch_errors = []
    if isinstance(batch, dict) and isinstance(batch.get("actions"), list):
        _fingerprint_attachments(batch["actions"])
        fetch_errors = _fetch_old_comment_texts(batch["actions"])
    errors = fetch_errors + validate(batch)
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


def _upload_attachment(a, token):
    boundary = f"----youtrackbatch{a['sha256'][:HASH_CHARS]}"
    name = os.path.basename(a["file"])
    with open(a["file"], "rb") as fh:
        content = fh.read()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{name}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8") + content + f"\r\n--{boundary}--\r\n".encode("utf-8")
    req = urllib.request.Request(
        f"{YOUTRACK_BASE}/api/issues/{a['issue']}/attachments?fields=id,name,size",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.status, resp.read().decode("utf-8", "replace")


def _fetch_project_id(token):
    req = urllib.request.Request(
        f"{YOUTRACK_BASE}/api/admin/projects?fields=id,shortName&$top=500",
        method="GET",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        projects = json.loads(resp.read().decode("utf-8", "replace"))
    for project in projects:
        if project.get("shortName") == PROJECT_SHORT_NAME:
            return project["id"]
    raise RuntimeError(f"project {PROJECT_SHORT_NAME} not found")


def _create_issue(a, project_id, token, on_created):
    """Create the issue, report its id through on_created before setting any field (so a failed
    field command still leaves the new id on record), then set the fields one command each."""
    status, body = _api(
        "POST",
        f"{YOUTRACK_BASE}/api/issues?fields=idReadable",
        {
            "project": {"id": project_id},
            "summary": a["summary"],
            "description": a.get("description", ""),
            "usesMarkdown": True,
        },
        token,
    )
    issue = json.loads(body)["idReadable"]
    on_created(issue)
    queries = [f"{name} {value}" for name, value in sorted(a.get("singleFields", {}).items())]
    queries += [
        f"{name} {value}" for name, values in sorted(a.get("fields", {}).items()) for value in values]
    if a.get("assignee"):
        queries.append(f"Assignee {a['assignee']}")
    for query in queries:
        status, _body = _api(
            "POST",
            f"{YOUTRACK_BASE}/api/commands",
            {"query": query, "issues": [{"idReadable": issue}]},
            token,
        )
    return issue, status


def _resolve_refs(a, created):
    """Copy of the action with every @ref replaced by the id its create action produced."""
    resolved = dict(a)
    for key in ("issue", "target"):
        value = str(resolved.get(key, ""))
        if value.startswith("@"):
            resolved[key] = created[value[1:]]
    return resolved


def _run_action(a, token):
    if a["type"] == "attach":
        return _upload_attachment(a, token)
    if a["type"] == "editComment":
        if _fetch_comment_text(a["issue"], a["commentId"], token) != a["oldText"]:
            raise RuntimeError(f"comment {a['commentId']} changed after staging; not overwritten")
        return _api(
            "POST",
            f"{YOUTRACK_BASE}/api/issues/{a['issue']}/comments/{a['commentId']}?fields=id",
            {"text": a["text"]},
            token,
        )
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

    # Resolve the project before any action runs, so a lookup failure leaves the stage unspent.
    project_id = None
    if any(a["type"] == "create" for a in actions):
        try:
            project_id = _fetch_project_id(token)
        except Exception as ex:
            print(f"ERROR: cannot resolve project {PROJECT_SHORT_NAME}: {ex}", file=sys.stderr)
            return 1

    results = []
    created = {}
    failed = False
    for i, a in enumerate(actions, 1):
        label = f"@{a['ref']}" if a["type"] == "create" else a["issue"]
        if failed:
            results.append({"action": i, "status": "skipped (earlier action failed)"})
            continue
        try:
            if a["type"] == "create":
                def on_created(issue, ref=a["ref"]):
                    created[ref] = issue
                    print(f"{i}. create @{ref}: created {issue}")
                issue, status = _create_issue(a, project_id, token, on_created)
                results.append({"action": i, "status": f"created {issue}, fields HTTP {status}"})
                continue
            resolved = _resolve_refs(a, created)
            label = resolved["issue"]
            status, _body = _run_action(resolved, token)
            results.append({"action": i, "status": f"HTTP {status}"})
            print(f"{i}. {a['type']} {label}: HTTP {status}")
        except urllib.error.HTTPError as ex:
            body = ex.read().decode("utf-8", "replace")[:500]
            results.append({"action": i, "status": f"FAILED HTTP {ex.code}: {body}"})
            print(f"{i}. {a['type']} {label}: FAILED HTTP {ex.code}: {body}", file=sys.stderr)
            failed = True
        except Exception as ex:
            results.append({"action": i, "status": f"FAILED: {ex}"})
            print(f"{i}. {a['type']} {label}: FAILED: {ex}", file=sys.stderr)
            failed = True
    if created:
        results.append({"created": created})

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
