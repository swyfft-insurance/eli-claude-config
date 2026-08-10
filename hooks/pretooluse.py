#!/usr/bin/env python3
"""PreToolUse hook: enforce deterministic rules from CLAUDE.md.

Receives JSON on stdin with tool_name and tool_input.
Exit 0 = allow, exit 2 + stderr = block.

This hook only hard-blocks. Rules-file injection was removed: dumping a rules
file alongside an allowed call does not change what the assistant does, so it
spent tokens for nothing. Guidance belongs in a block that stops the call.
"""

import json
import os
import re
import sys

RULES_DIR = os.path.expanduser("~/.claude/rules")


def check_askuserquestion_warnings(tool_input):
    """Warn when AskUserQuestion looks like it's smuggling unauthorized action options.

    Common failure: the assistant proposes two actions it wants to take, then asks the
    user to "pick which one". That's launders a scope decision the user never authorized.
    Detect option labels that contain action verbs.
    """
    warnings = []
    action_verb_pattern = re.compile(
        r"\b(fix|apply|update|add|remove|edit|create|implement|copy|delete|rename|modify|"
        r"replace|overwrite|migrate|move|push|post|send|upload|drop|insert)\b",
        re.IGNORECASE,
    )
    questions = tool_input.get("questions", []) or []
    for q in questions:
        if not isinstance(q, dict):
            continue
        options = q.get("options", []) or []
        action_option_count = 0
        for opt in options:
            if not isinstance(opt, dict):
                continue
            label = opt.get("label", "") or ""
            if action_verb_pattern.search(label):
                action_option_count += 1
        if action_option_count >= 2:
            warnings.append(
                "AskUserQuestion has 2+ options whose labels contain action verbs "
                "(fix/apply/update/edit/etc.). You may be asking the user to disambiguate "
                "between actions YOU proposed, instead of answering their question or "
                "asking a neutral clarification. Re-read core-behavior.md § Gate 1."
            )
            break
    return warnings

APPROVAL_STATE_PATH = os.path.expanduser("~/.claude/.post-approval-state.json")
APPROVAL_OVERRIDE_PATH = os.path.expanduser("~/.claude/.approve-next-post")

# Tools that publish to a human outside this conversation.
GATED_POST_TOOLS = {
    "mcp__YouTrackNative__add_issue_comment",
    "mcp__YouTrackNative__create_issue",
    "mcp__YouTrackNative__update_issue",
    "mcp__slack__slack_send_message",
}

GATED_POST_COMMAND_PATTERNS = (
    (r"\bgh\s+pr\s+(create|comment|edit|review)\b", "gh pr create/comment/edit/review"),
    (r"\bgh\s+issue\s+(create|comment|edit)\b", "gh issue create/comment/edit"),
    (r"\bcurl\b[^|;]*\b(POST|PUT)\b[^|;]*youtrack", "curl POST/PUT to the YouTrack API"),
    (r"\bcurl\b[^|;]*youtrack[^|;]*\b(POST|PUT)\b", "curl POST/PUT to the YouTrack API"),
)

# The whole message must BE an approval. "yes but reword the second paragraph" is an edit,
# so anything carrying extra content deliberately fails to match.
#
# Three shapes count. A bare affirmation ("yes"). A short imperative naming the action
# ("create the pr", "post the comment") — a direct order is at least as explicit as "yes".
# And an /eli--ask-properly answer ("1a", "1a, 2b"), since that skill instructs the user to
# reply in exactly that form and a gate the sanctioned reply format can't satisfy is a trap.
# Appended to every Gate 2 block. Getting blocked reliably triggers a hunt for another way
# through — a different transport (MCP vs curl vs gh), a read of this file to find a phrase that
# matches, asking the user to run the publish by hand. Every one of those defeats the gate, and
# reaching for one after being blocked is worse than the original attempt.
NO_WORKAROUND = (
    "\n\nDo NOT try to get around this block. No switching transport (MCP, curl, gh, a script), "
    "no reading this hook to find wording that passes, no handing the command to the user to run. "
    "STOP and ASK.\n"
    "Ask for ONE action, in a question short enough that a bare 'yes' answers it. Bundling "
    "several actions into one request is what causes this: the user's reply then has to name them, "
    "so it carries extra content and cannot match a bare approval."
)

APPROVAL_RE = re.compile(
    r"^("
    r"(y|yes|yep|yeah|yup|ya|ok|okay|k|sure|go|go ahead|do it|send|send it|post|post it|"
    r"ship it|approved|approve|lgtm|sounds good|please do|yes please|looks good)"
    r"|"
    r"(create|make|open|post|send|submit|file|add|update|move|do)\s+(the\s+|it\s*)?"
    r"(pr|pull request|comment|reply|message|msg|issue|ticket|it)"
    r"|"
    r"\d+[a-z](\s*[, ]\s*\d+[a-z])*"
    r")[\s.!]*$",
    re.IGNORECASE,
)


def last_human_message(transcript_path):
    """Return (uuid, text) of the most recent message a human actually typed.

    Tool results also arrive as type 'user' records, but they carry tool_result blocks and
    no text, so they're skipped — otherwise the newest "user message" would almost always
    be a tool result rather than anything the user said.
    """
    if not transcript_path or not os.path.exists(transcript_path):
        return (None, None)
    found = (None, None)
    try:
        with open(transcript_path, encoding="utf-8-sig") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if rec.get("type") != "user" or rec.get("isMeta"):
                    continue
                content = rec.get("message", {}).get("content")
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    text = "".join(
                        b.get("text", "") for b in content
                        if isinstance(b, dict) and b.get("type") == "text"
                    )
                else:
                    continue
                text = re.sub(r"<system-reminder>.*?</system-reminder>", "", text, flags=re.DOTALL)
                if text.strip():
                    found = (rec.get("uuid"), text.strip())
    except Exception:
        return (None, None)
    return found


def read_spent_approvals():
    try:
        with open(APPROVAL_STATE_PATH, encoding="utf-8-sig") as fh:
            return json.load(fh).get("spent", [])
    except Exception:
        return []


def spend_approval(uuid):
    """Mark an approval consumed so one go-ahead authorizes exactly one publish."""
    max_remembered = 50
    spent = read_spent_approvals()
    spent.append(uuid)
    try:
        with open(APPROVAL_STATE_PATH, "w", encoding="utf-8") as fh:
            json.dump({"spent": spent[-max_remembered:]}, fh)
    except Exception:
        pass


def check_post_approval(data, tool_name, tool_input):
    """Block anything that publishes outside this conversation without an explicit go-ahead.

    Gate 2 asks for a draft and a clear approval before posting. Stating that rule in the
    prompt has not held — the failure is always the same shape: the user sends an edit to
    the draft and the edit gets read as consent. This checks the one fact that settles it,
    outside the model's own judgment: did a human type an approval since the last publish?
    Returns a block message, or None to allow.
    """
    label = None
    if tool_name in GATED_POST_TOOLS:
        label = tool_name
    elif tool_name in ("Bash", "PowerShell"):
        cmd = tool_input.get("command", "") or ""
        for pattern, description in GATED_POST_COMMAND_PATTERNS:
            if re.search(pattern, cmd, re.IGNORECASE):
                label = description
                break
    if not label:
        return None

    # Moving a ticket to Review is workflow bookkeeping, not a publishing decision: the PR is
    # already up, so the ticket is in Review by definition. Asking wastes a turn after the user
    # believes the work is done. Scoped to a Stage->Review update carrying nothing else.
    if tool_name == "mcp__YouTrackNative__update_issue":
        fields = tool_input.get("customFields") or {}
        stage_only = list(fields.keys()) == ["Stage"] and fields.get("Stage") == "Review"
        carries_nothing_else = not tool_input.get("summary") and not tool_input.get("description")
        if stage_only and carries_nothing_else:
            return None

    # One-shot manual release, for when the transcript can't be read.
    if os.path.exists(APPROVAL_OVERRIDE_PATH):
        try:
            os.remove(APPROVAL_OVERRIDE_PATH)
        except Exception:
            pass
        return None

    uuid, text = last_human_message(data.get("transcript_path"))
    if not uuid:
        return (
            f"BLOCKED ({label}): the transcript could not be read, so the hook cannot confirm "
            "the user approved this. Ask for approval, then have the user create "
            f"{APPROVAL_OVERRIDE_PATH} to release a single send." + NO_WORKAROUND
        )
    if not APPROVAL_RE.match(text):
        max_preview = 80
        preview = text if len(text) <= max_preview else text[:max_preview] + "..."
        return (
            f"BLOCKED ({label}): the user's most recent message is not an approval. It reads:\n"
            f"  {preview!r}\n"
            "An edit to the draft, a question, or a correction is NOT consent. Put the draft in "
            "your response and wait for an explicit go-ahead. See core-behavior.md § Gate 2."
            + NO_WORKAROUND
        )
    if uuid in read_spent_approvals():
        return (
            f"BLOCKED ({label}): that approval was already used for an earlier publish. "
            "One approval authorizes one send — ask again before publishing anything else."
            + NO_WORKAROUND
        )
    spend_approval(uuid)
    return None


# The PR title is the only input to the YouTrack stage automation
# (.github/workflows/youtrack-update-on-merge.yml reads it and nothing else), so a ticket the PR
# covers but leaves out of the title never advances, and the wrong stage surfaces weeks later.
PRODUCT_LINE_RE = re.compile(
    r"\(\s*(?:HO|CO|Flood|DBB)(?:\s*,\s*(?:HO|CO|Flood|DBB))*\s*\)",
    re.IGNORECASE,
)
PARTIAL_TICKET_MARKER = "(partially delivered)"


def extract_flag_value(cmd, flag):
    """Return a CLI flag's value with any surrounding quotes stripped, or None if absent."""
    match = re.search(rf"{re.escape(flag)}(?:=|\s+)(\"[^\"]*\"|'[^']*'|\S+)", cmd)
    if not match:
        return None
    value = match.group(1)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value


def covered_tickets(body):
    """Ticket IDs the PR covers, read from the body's '## Ticket Link' section.

    A line tagged '(partially delivered)' names a ticket this PR does not finish — an epic whose
    children aren't all here — so it is excluded: it stays out of the title and its stage stays put.
    Returns the ticket list in document order, deduplicated.
    """
    section = re.search(r"^##\s+Ticket Link\s*$(.*?)(?=^##\s|\Z)", body, re.M | re.S)
    if not section:
        return []
    tickets = []
    for line in section.group(1).splitlines():
        if PARTIAL_TICKET_MARKER in line.lower():
            continue
        for ticket in re.findall(r"\bSW-\d+\b", line):
            if ticket not in tickets:
                tickets.append(ticket)
    return tickets


def check_pr_create_title(cmd):
    """Block `gh pr create` when the title omits a covered ticket or the product line."""
    if not re.search(r"\bgh\s+pr\s+create\b", cmd) or "--help" in cmd:
        return None

    title = extract_flag_value(cmd, "--title")
    if title is None:
        return (
            "BLOCKED (gh pr create): no --title. The YouTrack automation reads ticket IDs out of "
            "the PR title, so it has to be explicit. See ~/.claude/rules/pr-creation.md."
        )

    body = extract_flag_value(cmd, "--body")
    body_file = extract_flag_value(cmd, "--body-file")
    if body_file:
        try:
            with open(os.path.expanduser(body_file), encoding="utf-8-sig") as fh:
                body = fh.read()
        except Exception as exc:
            return (
                f"BLOCKED (gh pr create): could not read --body-file {body_file!r} ({exc}). "
                "The title check needs the body to know which tickets the PR covers."
            )
    if not body:
        return (
            "BLOCKED (gh pr create): no --body-file. pr-creation.md requires the body in a file "
            "under the ticket's artifacts/pr/, and the title check reads it to find covered tickets."
        )

    tickets = covered_tickets(body)
    if not tickets:
        return (
            "BLOCKED (gh pr create): the body has no '## Ticket Link' section listing SW- tickets, "
            "so which tickets the PR covers can't be verified. Follow "
            ".github/pull_request_template.md."
        )

    missing = [ticket for ticket in tickets if f"[{ticket}]" not in title]
    if missing:
        return (
            "BLOCKED (gh pr create): the title omits "
            f"{len(missing)} of the {len(tickets)} tickets the body says this PR covers: "
            f"{', '.join(missing)}.\n"
            "youtrack-update-on-merge.yml moves stages off the title alone, so an omitted ticket "
            "silently never advances. Add each as [SW-XXXXX].\n"
            "A ticket this PR does NOT finish (an epic whose children aren't all here) belongs out "
            f"of the title — tag its Ticket Link line '{PARTIAL_TICKET_MARKER}' instead."
        )

    if not PRODUCT_LINE_RE.search(title) and "# no-product-line" not in cmd:
        return (
            "BLOCKED (gh pr create): the title names no product line. Add it in parens after the "
            "ticket brackets: (HO), (CO), (Flood), (DBB), or (HO, CO) for several.\n"
            "  [SW-54114] [SW-54115] (HO) Aug 8, 2026 base rate updates for AL and FL\n"
            "If the PR genuinely has no product line (build, CI, tooling), append "
            "'# no-product-line' to the command."
        )

    return None


def main():
    try:
        data = json.load(sys.stdin)  # utf8-ok: stdin JSON from Claude Code, never a file/BOM
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    messages = []

    # BLOCK: publishing outside this conversation without an explicit, unspent approval.
    post_block = check_post_approval(data, tool_name, tool_input)
    if post_block:
        print(post_block, file=sys.stderr)
        sys.exit(2)

    # BLOCK: SolarWinds MCP tools — must use /search-logs skill instead.
    if re.search(r"^mcp__solarwinds__", tool_name):
        print(
            "BLOCKED: Do not call SolarWinds MCP tools directly. "
            "Use the /search-logs skill, which calls ~/.claude/scripts/Search-SolarWinds.ps1. "
            "The MCP tool has known issues with date ranges and Invoke-RestMethod.",
            file=sys.stderr,
        )
        sys.exit(2)

    # BLOCK: YouTrack ticket reads — must use the /eli--read-ticket skill instead.
    # Reading a ticket is one usage: /eli--read-ticket returns the full ticket (description, every
    # comment, custom fields incl. Stage, attachments) — the same complete view a human gets
    # opening it. get_issue / get_issue_comments invite partial reads that miss context.
    # /eli--read-ticket runs read-ticket.py (direct REST), not these MCP tools, so it's unaffected.
    # No bypass: an MCP call has no command string to carry a token (matches the SolarWinds block).
    if tool_name in ("mcp__YouTrackNative__get_issue", "mcp__YouTrackNative__get_issue_comments"):
        print(
            "BLOCKED: Do not read YouTrack tickets via the MCP get tools. "
            "Use the /eli--read-ticket skill — it returns the full ticket (description, all comments, "
            "custom fields incl. Stage, attachments), the same view you get opening the ticket. "
            "It accepts the readable ID (SW-XXXXX) or the internal entity ID (2-XXXXX). "
            "search_issues and the write tools are unaffected.",
            file=sys.stderr,
        )
        sys.exit(2)

    # AskUserQuestion-specific guardrail
    if tool_name == "AskUserQuestion":
        for warning in check_askuserquestion_warnings(tool_input):
            messages.append(f"⚠️ ASKUSERQUESTION WARNING: {warning}")

    if tool_name in ("Bash", "PowerShell"):
        cmd = tool_input.get("command", "")

        # BLOCK: pwsh/powershell/.ps1 invocations through Bash — use the PowerShell tool instead.
        # CLAUDE_CODE_USE_POWERSHELL_TOOL is set, so the PowerShell tool is available.
        # Append "# via-bash-pwsh" to bypass for the rare case bash semantics are required.
        if tool_name == "Bash" and "# via-bash-pwsh" not in cmd:
            pwsh_at_start = re.search(r"^\s*(pwsh|powershell)(\.exe)?\s", cmd)
            ps1_invocation = re.search(r"^\s*[&.]?\s*['\"]?[^'\"\s]*\.ps1\b", cmd)
            if pwsh_at_start or ps1_invocation:
                print(
                    "BLOCKED: Do not invoke pwsh, powershell, or .ps1 scripts through the Bash tool. "
                    "Use the PowerShell tool directly — it runs commands in native pwsh on Windows.\n\n"
                    "Example with the PowerShell tool:\n"
                    "  command: & \"$HOME/.claude/scripts/Build-Solution.ps1\"\n\n"
                    "If bash semantics are genuinely required, append \"# via-bash-pwsh\" to the command.",
                    file=sys.stderr,
                )
                sys.exit(2)

        # BLOCK: PowerShell here-strings (@'...'@ / @"..."@) in a Bash command. Bash does not
        # parse them, so the @ delimiters land inside the payload. This has silently corrupted
        # git commit messages more than once.
        # The opening delimiter alone is the block signal: `@'` ending a line is never valid Bash,
        # so how the text closes is irrelevant. Requiring a matching close let a command through
        # whenever anything followed the closing delimiter (`'@ 2>&1 | tail -20`).
        if tool_name == "Bash":
            if re.search(r"@['\"]\s*$", cmd, re.M):
                print(
                    "BLOCKED: PowerShell here-string syntax (@'...'@) in a Bash command. Bash does "
                    "not parse it, so the @ delimiters end up inside your text — this has corrupted "
                    "commit messages before.\n\n"
                    "For a multi-line git commit message, write the message to a file first:\n"
                    "  git commit -F <path-to-message-file>\n\n"
                    "For other multi-line text in Bash, use a real heredoc:\n"
                    "  cat <<'EOF' > file\n  ...\n  EOF\n\n"
                    "Or run the command with the PowerShell tool, where @'...'@ is valid.",
                    file=sys.stderr,
                )
                sys.exit(2)

        # BLOCK: Direct SolarWinds API calls — must use /search-logs skill instead.
        # Allow calls from the Search-SolarWinds.ps1 script itself.
        if re.search(r"api\.na-01\.cloud\.solarwinds\.com", cmd) and not re.search(r"Search-SolarWinds", cmd):
            print(
                "BLOCKED: Do not call the SolarWinds API directly. "
                "Use the /search-logs skill, which calls ~/.claude/scripts/Search-SolarWinds.ps1.",
                file=sys.stderr,
            )
            sys.exit(2)

        # BLOCK: lazy YouTrack ticket reads via the REST API — must use /eli--read-ticket.
        # /eli--read-ticket is the one-stop ticket read (description, comments, custom fields,
        # attachments, field-change history, tags). A raw GET dodges it — both the by-id form
        # (/api/issues/{id}, /comments, /activities, ...) and the search/list form
        # (/api/issues?query=...&fields=description,comments(...)). Hence /api/issues[/?].
        # Writes stay open: POST/PUT/DELETE (e.g. the /api/commands Release Stage NA call,
        # which isn't under /api/issues anyway) are not reads. read-ticket.py reads via Python
        # urllib, so its command ("python .../read-ticket.py") contains no /api/issues.
        is_yt_issue_read = re.search(r"youtrack[^\n]*?/api/issues[/?]", cmd)
        is_yt_write = re.search(
            r"-X\s*(POST|PUT|DELETE)|-XPOST|-XPUT|--request\s+(POST|PUT|DELETE)|-Method\s+(Post|Put|Delete)",
            cmd,
            re.IGNORECASE,
        )
        if is_yt_issue_read and not is_yt_write and "read-ticket.py" not in cmd:
            print(
                "BLOCKED: Do not read YouTrack tickets via the REST API directly. "
                "Use the /eli--read-ticket skill — the single source for everything about a ticket "
                "(description, all comments, custom fields incl. Stage, attachments, and "
                "field-change history). It accepts SW-XXXXX or the internal 2-XXXXX id. "
                "Writes (POST/PUT to the command/issue API) are unaffected.",
                file=sys.stderr,
            )
            sys.exit(2)

        # BLOCK: truncating /eli--read-ticket output - the skill returns the FULL ticket on purpose.
        # Piping read-ticket.py through head/tail/more/Select-Object -First clips the description,
        # ACs, or comments - the exact content the skill exists to deliver. If the JSON is large,
        # parse out the fields you need (python -c over the parsed object); never lop off the end.
        if "read-ticket.py" in cmd and re.search(
            r"\|\s*(head|tail|more)\b|Select-Object\s+-(First|Last)\b|Select\s+-(First|Last)\b",
            cmd,
        ):
            print(
                "BLOCKED: Do not pipe /eli--read-ticket output through head, tail, more, or "
                "Select-Object -First/-Last. The skill returns the full ticket on purpose; "
                "clipping it drops the description, acceptance criteria, or comments, the exact "
                "content the skill exists to deliver. If the JSON is large, parse out the fields "
                "you need (e.g. python -c over the parsed object); never truncate the end.",
                file=sys.stderr,
            )
            sys.exit(2)

        # BLOCK: Seed scripts must go through Run-Seed.ps1 wrapper, which captures
        # full output to a deterministic file so completion is verifiable. Direct
        # invocation produces truncated stdout that hides whether the seed actually
        # completed — repeatedly led the agent to guess by running tests.
        if re.search(r"Seed-(Elements|Database)-Local\.ps1", cmd) and "Run-Seed.ps1" not in cmd:
            print(
                "BLOCKED: Do NOT invoke Seed-Database-Local.ps1 or Seed-Elements-Local.ps1 directly. "
                "Use the Run-Seed.ps1 wrapper, which captures full output to a deterministic log file "
                "and prints the tail + exit code so completion is verifiable:\n\n"
                "  pwsh -NoProfile -File \"$HOME/.claude/scripts/Run-Seed.ps1\" -Mode database\n"
                "  pwsh -NoProfile -File \"$HOME/.claude/scripts/Run-Seed.ps1\" -Mode elements\n\n"
                "The /eli--seed skill instructions reflect this. Do NOT bypass this block — it exists "
                "because direct invocation truncates output and hides failures.",
                file=sys.stderr,
            )
            sys.exit(2)

        # BLOCK: UI acceptance tests must go through the /eli--run-ui-acceptance-tests-local skill.
        # Skill: ~/.claude/skills/eli--run-ui-acceptance-tests-local/SKILL.md
        if (
            (re.search(r"dotnet\s+test", cmd) and re.search(r"Swyfft\.Web\.Ui\.AcceptanceTests", cmd))
            or (re.search(r"Run-DotnetTest\.ps1", cmd) and re.search(r"Swyfft\.Web\.Ui\.AcceptanceTests", cmd))
            or re.search(r"(pwsh|powershell)[^\n]*Scripts[/\\]TestRunners[/\\](WebUiAcceptanceTests-|CriticalTests-)", cmd)
            or re.search(r"(&|\.[\\/])[^\n]*Scripts[/\\]TestRunners[/\\](WebUiAcceptanceTests-|CriticalTests-)", cmd)
        ) and "# via-run-ui-acceptance-tests-local" not in cmd:
            print(
                "BLOCKED: Do not run UI acceptance tests directly. "
                "Use the /eli--run-ui-acceptance-tests-local skill "
                "(~/.claude/skills/eli--run-ui-acceptance-tests-local/SKILL.md). "
                "It kills the site, builds the solution, starts the site, "
                "runs the test, and kills the site again — every time.",
                file=sys.stderr,
            )
            sys.exit(2)

        # BLOCK: All builds must go through Build-Solution.ps1.
        # The script captures ALL error types (CS, IDE, SWYF, etc.) — raw dotnet build + grep misses non-CS errors.
        if re.search(r"dotnet\s+build", cmd) \
           and not re.search(r"Build-Solution\.ps1|# via-build-script", cmd):
            print(
                "BLOCKED: Do not run dotnet build directly. "
                "Use Build-Solution.ps1 which captures ALL error types (CS, IDE, SWYF, etc.).\n\n"
                "Example:\n"
                "  pwsh -NoProfile -File \"$HOME/.claude/scripts/Build-Solution.ps1\"\n\n"
                "(builds Swyfft.slnx — the script no longer accepts a -Solution override)",
                file=sys.stderr,
            )
            sys.exit(2)

        # ALLOW: read-only test discovery. Listing tests or printing help/info never executes
        # tests and captures no results, so the Run-DotnetTest.ps1 / Tee / trx requirements below
        # don't apply. Recognized via the xUnit v3 native `-list <level>` (full/classes/methods/
        # tests/traits), MTP `--list-tests`, `--help`/`--info`, OR the Run-DotnetTest.ps1 /
        # Run-PreBindValidation.ps1 wrapper param `-ListTests` (which the wrapper translates to the
        # native `-list` form). Case-insensitive because PowerShell params are.
        is_readonly_test_query = bool(
            re.search(
                r"-list\s+(full|classes|methods|tests|traits)|--list-tests|-ListTests\b|--help|--info",
                cmd,
                re.IGNORECASE,
            )
        )

        # BLOCK: All test execution must go through Run-DotnetTest.ps1.
        # Scripts call it internally via pwsh -File, so "dotnet test" never appears
        # in their bash command. Raw "dotnet test" commands are always blocked.
        if re.search(r"dotnet\s+test|IntegrationTests\.exe|UnitTests\.exe", cmd) \
           and not re.search(r"# via-run-dotnet-test", cmd) \
           and not is_readonly_test_query:
            print(
                "BLOCKED: Do not run dotnet test directly. "
                "Use Run-DotnetTest.ps1 which enforces deterministic output file naming, "
                "Tee-Object, --output Detailed, and --report-trx.\n\n"
                "Example:\n"
                "  pwsh -NoProfile -File \"$HOME/.claude/scripts/Run-DotnetTest.ps1\" "
                "-Project \"Swyfft.Services.Excel.IntegrationTests\" "
                "-FilterTrait \"TestGroup=ByPerilTests\"\n\n"
                "For prebind validation: /eli--prebind-validation skill\n"
                "For audit diagnostics: /eli--byperil-audit-diagnostic skill",
                file=sys.stderr,
            )
            sys.exit(2)

        # BELT-AND-SUSPENDERS: Excel integration tests must scope to ByPeril tests.
        # Unfiltered runs include commercial tests (45+ min). Allows --filter-trait ByPerilTests
        # OR the specific HomeownerExcelQuoteAuditDiagnosticTests class (which lost its ByPerilTests trait in PR #20002)
        # OR CommercialExcelQuoteAuditDiagnosticTests (SW-53865; both renamed in SW-53915).
        # Matches both raw `dotnet test` invocations and `Run-DotnetTest.ps1` wrapper calls;
        # accepts the trait passed as either `--filter-trait` (CLI) or `-FilterTrait` (PowerShell wrapper param).
        is_dotnet_test = re.search(r"dotnet\s+test|IntegrationTests\.exe|UnitTests\.exe|Run-DotnetTest\.ps1", cmd)
        has_byperil_trait = (
            re.search(r'--filter-trait\s+["\']?TestGroup=ByPerilTests', cmd)
            or re.search(r'-FilterTrait\s+["\']?TestGroup=ByPerilTests', cmd)
        )
        # Commercial ByPeril Excel tests carry TestGroup=Commercial, not ByPerilTests. Passing
        # -IsCommercial to Run-DotnetTest.ps1 is a deliberate opt-in to run them (can't be hit by
        # accident), so allow it through the guard.
        is_commercial_optin = re.search(r"-IsCommercial\b", cmd)
        if is_dotnet_test and re.search(r"Excel\.IntegrationTests", cmd) \
           and not has_byperil_trait \
           and not is_commercial_optin \
           and not is_readonly_test_query \
           and not re.search(r"(Homeowner|Commercial)ExcelQuoteAuditDiagnosticTests", cmd):
            print(
                "BLOCKED: Excel integration tests must include --filter-trait \"TestGroup=ByPerilTests\" "
                "(or -FilterTrait via Run-DotnetTest.ps1), pass -IsCommercial for the commercial suite, "
                "or target the Homeowner/Commercial ExcelQuoteAuditDiagnosticTests classes specifically. "
                "Running without this filter includes commercial tests which take an eternity. "
                "If you truly need all tests, ask the user to confirm.",
                file=sys.stderr,
            )
            sys.exit(2)

        # BELT-AND-SUSPENDERS: dotnet test must capture output with Tee-Object, --output Detailed, and --report-trx.
        if re.search(r"dotnet\s+test|IntegrationTests\.exe|UnitTests\.exe", cmd) \
           and not is_readonly_test_query:
            missing = []
            if not re.search(r"Tee-Object", cmd):
                missing.append("Tee-Object")
            if not re.search(r"--output\s+Detailed", cmd):
                missing.append("--output Detailed")
            if not re.search(r"--report-trx", cmd):
                missing.append("--report-trx")
            if missing:
                rules_path = os.path.join(RULES_DIR, "testing-execution.md")
                rules_content = ""
                try:
                    with open(rules_path) as f:
                        rules_content = f.read()
                except FileNotFoundError:
                    pass
                print(
                    f"BLOCKED: dotnet test is missing: {', '.join(missing)}. "
                    "Re-read the rules below and retry.\n\n"
                    f"=== RULES: testing-execution.md ===\n{rules_content}",
                    file=sys.stderr,
                )
                sys.exit(2)

        # BLOCK: git commit --amend — always create new commits.
        if re.search(r"git\s+commit\s+.*--amend|git\s+commit\s+--amend", cmd):
            print(
                "BLOCKED: Do not amend commits. Always create new commits. "
                "Amending rewrites history and is especially dangerous after pushing.",
                file=sys.stderr,
            )
            sys.exit(2)

        # BLOCK: git push --force / --force-with-lease — destructive to remote history.
        if re.search(r"git\s+push\s+.*--force|git\s+push\s+.*-f\b", cmd):
            print(
                "BLOCKED: Do not force-push. This rewrites remote history. "
                "If you need to fix a commit, create a new commit instead.",
                file=sys.stderr,
            )
            sys.exit(2)

        # BLOCK: Bulk merge conflict resolution — must resolve one file at a time.
        # The /resolve-conflicts skill appends "# via-resolve-conflicts-skill" to bypass.
        if re.search(r"git\s+checkout\s+--(ours|theirs)", cmd) and "# via-resolve-conflicts-skill" not in cmd:
            # Count file paths after --ours/--theirs (split on whitespace, count quoted or unquoted paths)
            # Simple heuristic: if the command has more than one file path, block it.
            parts = re.split(r"git\s+checkout\s+--(?:ours|theirs)\s+", cmd, maxsplit=1)
            if len(parts) > 1:
                file_args = parts[1].strip()
                # Count files: split by unquoted whitespace or by closing quote + whitespace
                file_count = len(re.findall(r'"[^"]+"|\'[^\']+\'|\S+', file_args))
                if file_count > 1:
                    print(
                        "BLOCKED: Do not bulk-resolve merge conflicts. "
                        "Resolve one file at a time — read the conflict markers, understand both sides, "
                        "then resolve. See ~/.claude/rules/merge-conflicts.md.",
                        file=sys.stderr,
                    )
                    sys.exit(2)

        # BLOCK: Raw git diff calls — must use /eli--diff skill.
        # The skill appends "# via-diff-skill" to bypass this block.
        if re.search(r"git\s+diff", cmd) and "# via-diff-skill" not in cmd:
            print(
                "BLOCKED: Do not run git diff directly. "
                "Use the /eli--diff skill:\n\n"
                "  /eli--diff local   — uncommitted changes (working tree vs last commit)\n"
                "  /eli--diff branch  — committed changes vs development\n\n"
                "You MUST choose one. No default.\n\n"
                "Do NOT dodge this by reconstructing the same view another way "
                "(git diff --name-only, git show <ref>:<file>, git log -p, etc.). "
                "Those commands are fine for their OWN jobs — reading a specific commit, "
                "a file at a ref, or history — but never to inspect the local or branch "
                "changes /eli--diff already covers. Use /diff.",
                file=sys.stderr,
            )
            sys.exit(2)

        # BLOCK: Raw PR comment reply/resolve calls — must use /eli--pr-feedback skill.
        if re.search(r"gh\s+api.*pulls.*/comments.*replies|resolveReviewThread", cmd) \
           and not re.search(r"pr-feedback", cmd):
            print(
                "BLOCKED: Do not reply to or resolve PR comments directly. "
                "Use the /eli--pr-feedback skill, which enforces research-then-draft-then-approve workflow.",
                file=sys.stderr,
            )
            sys.exit(2)

        # BLOCK: Raw PR review/comment WRITES — must use ~/.claude/scripts/pr-review.py.
        # Writes only: `gh pr review`, `gh pr comment`, and `gh api` POSTs that CREATE a
        # review/comment. Reads are deliberately left alone — `gh pr view --json
        # reviews,comments`, any `gh api ... GET`, and the script's own read-back all pass.
        gh_pr_write = re.search(r"\bgh\s+pr\s+(review|comment)\b", cmd)
        gh_api_create = (
            re.search(r"\bgh\s+api\b", cmd)
            and re.search(r"pulls/\d+/(reviews|comments)\b", cmd)
            and re.search(r"(-X\s*POST|-XPOST|--method\s+POST)", cmd)
        )
        if (gh_pr_write or gh_api_create) and not re.search(r"pr-review\.py|pr-feedback", cmd):
            print(
                "BLOCKED: Do not post PR reviews/comments directly. "
                "Use ~/.claude/scripts/pr-review.py (approve | comment --inline <json> | "
                "request-changes --body-file <f>). It sends bodies verbatim via `gh api "
                "--input` and reads each one back to confirm it landed — preventing the "
                "literal-@file / mangled-body class of bug. Reads (gh pr view, gh api GET) "
                "are not blocked.",
                file=sys.stderr,
            )
            sys.exit(2)

        # BLOCK: a `gh pr create` title that omits a covered ticket or the product line.
        pr_title_block = check_pr_create_title(cmd)
        if pr_title_block:
            print(pr_title_block, file=sys.stderr)
            sys.exit(2)

        # BLOCK: unscoped `git log` — the whole-repo history sweep (research strategy, not safety).
        # git blame (file-scoped) and git show (object-scoped) are always fine; only an
        # unscoped/unbounded `git log` is blocked. The /eli--file-history skill appends
        # "# via-file-history-skill" to bypass. Allowed when scoped (path / -L) or bounded
        # (revision range / commit limit).
        if re.search(r"git\s+log\b", cmd) and "# via-file-history-skill" not in cmd:
            has_pickaxe = re.search(r"\s-[SG]\b", cmd)
            has_path = re.search(r"\s--\s\S", cmd)
            has_range = re.search(r"\.\.", cmd)
            has_limit = re.search(r"--max-count|\s-n\s+\d|\s-\d+\b", cmd)
            has_line_log = re.search(r"\s-L\b", cmd)
            scoped_or_bounded = has_path or has_range or has_limit or has_line_log
            if (has_pickaxe and not has_path) or not scoped_or_bounded:
                print(
                    "BLOCKED: unscoped `git log` walks the ENTIRE repo history (the wasteful sweep). "
                    "Scope or bound it, or use the /eli--file-history skill:\n"
                    "  git log -L :Method:path/File.cs        (one method's history)\n"
                    "  git blame -L <a>,<b> -- path/File.cs    (who/when changed lines)\n"
                    "  git log -S \"<string>\" -- path/File.cs   (when a string entered/left a file)\n"
                    "  git log development..HEAD               (commits on this branch — PR review)\n"
                    "  git log --oneline -20                   (recent commits, bounded)\n"
                    "Commit messages carry the SW- prefix (= the ticket); else trace the PR via gh.",
                    file=sys.stderr,
                )
                sys.exit(2)

        # BLOCK: Python file reads without utf-8-sig. Windows files routinely carry a UTF-8 BOM
        # (.NET/PowerShell/VS/DumpRater output); plain 'utf-8' leaves the BOM at char 0 so json.load
        # dies "Expecting value: line 1 column 1". utf-8-sig strips a BOM if present and is identical
        # to utf-8 when absent, so it's always correct for READS. Keyed on read APIs only — writes
        # (json.dump/to_csv/write_text) never match, so we never push a BOM into output. Append
        # "# utf8-ok" for a deliberate non-utf8 read (binary/latin-1/stdin).
        if re.search(r"\bpython[0-9.]*\b", cmd) \
           and re.search(r"json\.load\(|\.read_text\(|pd\.read_(csv|json|excel)\b|csv\.reader\b", cmd) \
           and not re.search(r"utf-8-sig|utf_8_sig", cmd) \
           and "# utf8-ok" not in cmd:
            print(
                "BLOCKED: Python file read without encoding='utf-8-sig'. On Windows most files carry "
                "a UTF-8 BOM (.NET/PowerShell/VS/DumpRater); plain 'utf-8' leaves \\ufeff at char 0 and "
                "json.load dies 'Expecting value: line 1 column 1'. Add encoding='utf-8-sig' (safe with "
                "or without a BOM). Deliberate non-utf8 read (binary/latin-1/stdin)? Append '# utf8-ok'.",
                file=sys.stderr,
            )
            sys.exit(2)

        messages.extend(check_bash_warnings(cmd))

    elif tool_name in ("Write", "Edit"):
        file_path = tool_input.get("file_path", "")

        # BLOCK: a .py file that reads a file without utf-8-sig — same BOM footgun as the inline
        # python block above, caught at write time before the script ever runs. Read APIs only;
        # writes never match. Append "# utf8-ok" for a deliberate non-utf8 read (binary/latin-1/stdin).
        edit_content = tool_input.get("content", "") if tool_name == "Write" else tool_input.get("new_string", "")
        edit_content = edit_content or ""
        if file_path.endswith(".py") \
           and re.search(r"json\.load\(|\.read_text\(|pd\.read_(csv|json|excel)\b|csv\.reader\b", edit_content) \
           and not re.search(r"utf-8-sig|utf_8_sig", edit_content) \
           and "# utf8-ok" not in edit_content:
            print(
                "BLOCKED: This .py reads a file without encoding='utf-8-sig'. Windows files carry a "
                "UTF-8 BOM (.NET/PowerShell/VS/DumpRater); plain 'utf-8' leaves \\ufeff at char 0 and "
                "json.load dies 'Expecting value: line 1 column 1'. Use encoding='utf-8-sig' for every "
                "read (safe with or without a BOM), or append '# utf8-ok' for a deliberate non-utf8 read.",
                file=sys.stderr,
            )
            sys.exit(2)

    if messages:
        print(json.dumps({"systemMessage": "\n\n".join(messages)}))

    sys.exit(0)


def check_bash_warnings(cmd):
    """Return list of warning messages for known Bash footguns."""
    warnings = []

    if re.search(r"\|\s*tee\s", cmd):
        warnings.append(
            "REMINDER: bash tee crashes on Windows. "
            "Use: pwsh -NoProfile -Command \"... 2>&1 | Tee-Object -FilePath 'C:\\...\\output.txt'\""
        )

    if re.search(r"git\s+checkout\s+--", cmd):
        warnings.append(
            "REMINDER: git checkout -- destroys uncommitted changes. "
            "If this is a 'commit minus X' situation, use git reset HEAD <file> to unstage instead."
        )

    if re.search(r"\bprintenv\b", cmd):
        warnings.append(
            "REMINDER: printenv silently truncates values containing '='. "
            "Use: powershell -NoProfile -Command \"[System.Environment]::GetEnvironmentVariable('VAR_NAME', 'User')\""
        )

    if re.search(r"\bmv\s+", cmd):
        warnings.append(
            "WARNING: mv silently fails on Windows. Use the safe pattern: "
            "cp source dest && ls dest && rm source"
        )

    if re.search(r"git\s+add\s+(-A|--all|\.)\b", cmd):
        warnings.append(
            "WARNING: Never git add -A/--all/. after a merge. "
            "Stage files individually by name."
        )

    if re.search(r"\|\s*tail\s+-", cmd):
        warnings.append(
            "WARNING: Piping to tail hides progress with run_in_background. "
            "Run the command directly, read the output file afterwards."
        )

    if re.search(r"pwsh.*(/tmp/|'/tmp/)", cmd):
        warnings.append(
            "WARNING: pwsh does not translate Unix /tmp/ paths. "
            "Use: C:\\Users\\eli.koslofsky\\AppData\\Local\\Temp\\"
        )

    if re.search(r"git\s+push", cmd):
        warnings.append(
            "WARNING: Before pushing, run git branch -vv first. "
            "Tracking must show origin/<your-branch>."
        )

    return warnings


if __name__ == "__main__":
    main()
