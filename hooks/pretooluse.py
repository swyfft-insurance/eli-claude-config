#!/usr/bin/env python3
"""PreToolUse hook: enforce deterministic rules from CLAUDE.md.

Receives JSON on stdin with tool_name and tool_input.
Exit 0 = allow, exit 2 + stderr = block.

Rules injection: when a tool call matches a known pattern, the corresponding
rules file from ~/.claude/rules/ is read and injected via systemMessage.
Rules are injected once per session per file (tracked via temp file),
except files in ALWAYS_INJECT which bypass dedup and inject every time.
"""

import json
import os
import re
import sys
import tempfile

RULES_DIR = os.path.expanduser("~/.claude/rules")

# Files that bypass session dedup — injected every time they match.
ALWAYS_INJECT = {"core-behavior.md", "pre-pr-review.md"}

# Session dedup: track which rules files have been injected.
# Keyed by Claude Code's session ID if available, otherwise by date.
# The CLAUDE_SESSION_ID env var is set by Claude Code; fall back to date for manual testing.
SESSION_KEY = os.environ.get("CLAUDE_SESSION_ID", "")
if not SESSION_KEY:
    from datetime import date
    SESSION_KEY = date.today().isoformat()
DEDUP_FILE = os.path.join(tempfile.gettempdir(), f"claude-rules-injected-{SESSION_KEY}")


def get_injected():
    """Return set of already-injected rules filenames."""
    try:
        with open(DEDUP_FILE) as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()


def mark_injected(filename):
    """Record that a rules file has been injected."""
    with open(DEDUP_FILE, "a") as f:
        f.write(filename + "\n")


def inject_rules(filename):
    """Read a rules file and return its content, or None if already injected or missing."""
    if filename not in ALWAYS_INJECT and filename in get_injected():
        return None
    path = os.path.join(RULES_DIR, filename)
    try:
        with open(path) as f:
            content = f.read()
        if filename not in ALWAYS_INJECT:
            mark_injected(filename)
        return content
    except FileNotFoundError:
        return None


# Bash command → rules file mappings
BASH_RULES = [
    (r"git\s+(push|commit|checkout|branch|merge|rebase|reset|cherry-pick)", "git-safety.md"),
    (r"git\s+(log|blame|show)", "investigation.md"),
    (r"gh\s+pr\s+(create|edit)", "pr-creation.md"),
    (r"gh\s+pr\s+review", "pr-theirs-review.md"),
    (r"gh\s+", "pr-mine-address-feedback.md"),
    (r"dotnet\s+test", "testing-execution.md"),
    # Seed is now blocked below — use /seed skill instead.
    (r"sqlcmd", "db-querying.md"),
    (r"git\s+(merge|checkout\s+--(ours|theirs))", "merge-conflicts.md"),
    (r"yde2xj08jm", "beta-prod-db.md"),
    (r"swyfftsqleastus2", "beta-prod-db.md"),
]

# Tool name → rules file mappings (for MCP tools and other non-Bash tools)
TOOL_RULES = [
    (r"^mcp__slack__slack_send_message$", "slack.md"),
    (r"^mcp__YouTrackNative__(create_issue|update_issue|add_issue_comment)$", "youtrack.md"),
    (r"^EnterPlanMode$", "plan-mode.md"),
    (r"^EnterPlanMode$", "core-behavior.md"),
    (r"^ExitPlanMode$", "coding-standards.md"),
    (r"^ExitPlanMode$", "core-behavior.md"),
    (r"^AskUserQuestion$", "communication.md"),
    (r"^AskUserQuestion$", "core-behavior.md"),
]


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

# Skill name → rules file mappings (for the Skill tool, dispatched by skill parameter)
SKILL_RULES = [
    (r"^review-pr$", "pre-pr-review.md"),
]

# File path patterns for Edit/Write → rules file mappings
FILE_RULES = [
    (r"\.claude[/\\]CLAUDE\.md$", "meta.md"),
    (r"\.claude[/\\]rules[/\\]", "meta.md"),
    (r"\.claude[/\\]projects[/\\].*[/\\]memory[/\\]", "meta.md"),
    (r"\.(cs|csproj)$", "coding-standards.md"),
    (r"\.(cs|csproj|ts|tsx|ps1|sql)$", "core-behavior.md"),
]


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    messages = []

    # BLOCK: SolarWinds MCP tools — must use /search-logs skill instead.
    if re.search(r"^mcp__solarwinds__", tool_name):
        print(
            "BLOCKED: Do not call SolarWinds MCP tools directly. "
            "Use the /search-logs skill, which calls ~/.claude/scripts/Search-SolarWinds.ps1. "
            "The MCP tool has known issues with date ranges and Invoke-RestMethod.",
            file=sys.stderr,
        )
        sys.exit(2)

    # Check tool name matches (MCP tools, EnterPlanMode, ExitPlanMode)
    for pattern, rules_file in TOOL_RULES:
        if re.search(pattern, tool_name):
            content = inject_rules(rules_file)
            if content:
                messages.append(f"=== RULES: {rules_file} ===\n{content}")

    # Skill tool: dispatch by skill parameter
    if tool_name == "Skill":
        skill_name = tool_input.get("skill", "")
        for pattern, rules_file in SKILL_RULES:
            if re.search(pattern, skill_name):
                content = inject_rules(rules_file)
                if content:
                    messages.append(f"=== RULES: {rules_file} ===\n{content}")

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

        # BLOCK: Direct SolarWinds API calls — must use /search-logs skill instead.
        # Allow calls from the Search-SolarWinds.ps1 script itself.
        if re.search(r"api\.na-01\.cloud\.solarwinds\.com", cmd) and not re.search(r"Search-SolarWinds", cmd):
            print(
                "BLOCKED: Do not call the SolarWinds API directly. "
                "Use the /search-logs skill, which calls ~/.claude/scripts/Search-SolarWinds.ps1.",
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
                "The /seed skill instructions reflect this. Do NOT bypass this block — it exists "
                "because direct invocation truncates output and hides failures.",
                file=sys.stderr,
            )
            sys.exit(2)

        # BLOCK: UI acceptance tests must go through the /run-ui-acceptance-tests-local skill.
        # Skill: ~/.claude/skills/run-ui-acceptance-tests-local/SKILL.md
        if (
            (re.search(r"dotnet\s+test", cmd) and re.search(r"Swyfft\.Web\.Ui\.AcceptanceTests", cmd))
            or (re.search(r"Run-DotnetTest\.ps1", cmd) and re.search(r"Swyfft\.Web\.Ui\.AcceptanceTests", cmd))
            or re.search(r"(pwsh|powershell)[^\n]*Scripts[/\\]TestRunners[/\\](WebUiAcceptanceTests-|CriticalTests-)", cmd)
            or re.search(r"(&|\.[\\/])[^\n]*Scripts[/\\]TestRunners[/\\](WebUiAcceptanceTests-|CriticalTests-)", cmd)
        ) and "# via-run-ui-acceptance-tests-local" not in cmd:
            print(
                "BLOCKED: Do not run UI acceptance tests directly. "
                "Use the /run-ui-acceptance-tests-local skill "
                "(~/.claude/skills/run-ui-acceptance-tests-local/SKILL.md). "
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
        # tests/traits), MTP `--list-tests`, or `--help`/`--info`. Canonical path: list via
        # `dotnet run -- -list <level>` (see Run-DotnetTest.ps1 -ListTests), NOT `dotnet test`.
        is_readonly_test_query = bool(
            re.search(r"-list\s+(full|classes|methods|tests|traits)|--list-tests|--help|--info", cmd)
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
                "For prebind captured asserts: /prebind-captured-asserts skill\n"
                "For audit diagnostics: /byperil-audit-diagnostic skill",
                file=sys.stderr,
            )
            sys.exit(2)

        # BELT-AND-SUSPENDERS: Excel integration tests must scope to ByPeril tests.
        # Unfiltered runs include commercial tests (45+ min). Allows --filter-trait ByPerilTests
        # OR the specific ByPerilQuoteAuditDiagnosticTests class (which lost its ByPerilTests trait in PR #20002).
        # Matches both raw `dotnet test` invocations and `Run-DotnetTest.ps1` wrapper calls;
        # accepts the trait passed as either `--filter-trait` (CLI) or `-FilterTrait` (PowerShell wrapper param).
        is_dotnet_test = re.search(r"dotnet\s+test|IntegrationTests\.exe|UnitTests\.exe|Run-DotnetTest\.ps1", cmd)
        has_byperil_trait = (
            re.search(r'--filter-trait\s+["\']?TestGroup=ByPerilTests', cmd)
            or re.search(r'-FilterTrait\s+["\']?TestGroup=ByPerilTests', cmd)
        )
        if is_dotnet_test and re.search(r"Excel\.IntegrationTests", cmd) \
           and not has_byperil_trait \
           and not is_readonly_test_query \
           and not re.search(r"ByPerilQuoteAuditDiagnosticTests", cmd):
            print(
                "BLOCKED: Excel integration tests must include --filter-trait \"TestGroup=ByPerilTests\" "
                "(or -FilterTrait via Run-DotnetTest.ps1) or target ByPerilQuoteAuditDiagnosticTests specifically. "
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

        # BLOCK: Raw git diff calls — must use /diff skill.
        # The skill appends "# via-diff-skill" to bypass this block.
        if re.search(r"git\s+diff", cmd) and "# via-diff-skill" not in cmd:
            print(
                "BLOCKED: Do not run git diff directly. "
                "Use the /diff skill with an explicit argument:\n\n"
                "  /diff local   — uncommitted changes (working tree vs last commit)\n"
                "  /diff branch  — committed changes vs development\n\n"
                "You MUST choose one. No default.",
                file=sys.stderr,
            )
            sys.exit(2)

        # BLOCK: Raw PR comment reply/resolve calls — must use /pr-feedback skill.
        if re.search(r"gh\s+api.*pulls.*/comments.*replies|resolveReviewThread", cmd) \
           and not re.search(r"pr-feedback", cmd):
            print(
                "BLOCKED: Do not reply to or resolve PR comments directly. "
                "Use the /pr-feedback skill, which enforces research-then-draft-then-approve workflow.",
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

        # BLOCK: unscoped `git log` — the whole-repo history sweep (research strategy, not safety).
        # git blame (file-scoped) and git show (object-scoped) are always fine; only an
        # unscoped/unbounded `git log` is blocked. The /file-history skill appends
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
                    "Scope or bound it, or use the /file-history skill:\n"
                    "  git log -L :Method:path/File.cs        (one method's history)\n"
                    "  git blame -L <a>,<b> -- path/File.cs    (who/when changed lines)\n"
                    "  git log -S \"<string>\" -- path/File.cs   (when a string entered/left a file)\n"
                    "  git log development..HEAD               (commits on this branch — PR review)\n"
                    "  git log --oneline -20                   (recent commits, bounded)\n"
                    "Commit messages carry the SW- prefix (= the ticket); else trace the PR via gh.",
                    file=sys.stderr,
                )
                sys.exit(2)

        messages.extend(check_bash_warnings(cmd))
        # Check bash command matches for rules injection
        for pattern, rules_file in BASH_RULES:
            if re.search(pattern, cmd):
                content = inject_rules(rules_file)
                if content:
                    messages.append(f"=== RULES: {rules_file} ===\n{content}")

    elif tool_name in ("Write", "Edit"):
        file_path = tool_input.get("file_path", "")
        # Check file path matches for rules injection
        for pattern, rules_file in FILE_RULES:
            if re.search(pattern, file_path):
                content = inject_rules(rules_file)
                if content:
                    messages.append(f"=== RULES: {rules_file} ===\n{content}")

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
