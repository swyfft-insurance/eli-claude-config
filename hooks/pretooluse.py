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
ALWAYS_INJECT = {"core-behavior.md"}

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

    if tool_name == "Bash":
        cmd = tool_input.get("command", "")

        # BLOCK: Direct SolarWinds API calls — must use /search-logs skill instead.
        # Allow calls from the Search-SolarWinds.ps1 script itself.
        if re.search(r"api\.na-01\.cloud\.solarwinds\.com", cmd) and not re.search(r"Search-SolarWinds", cmd):
            print(
                "BLOCKED: Do not call the SolarWinds API directly. "
                "Use the /search-logs skill, which calls ~/.claude/scripts/Search-SolarWinds.ps1.",
                file=sys.stderr,
            )
            sys.exit(2)

        # BLOCK: Seed scripts must go through /seed skill.
        # The skill appends "# via-seed-skill" to bypass this block.
        if re.search(r"Seed-(Elements|Database)-Local\.ps1", cmd) and "# via-seed-skill" not in cmd:
            print(
                "BLOCKED: Do NOT run seed scripts without the /seed skill. "
                "You MUST use /seed — it determines the correct script, "
                "clears seeding history when needed, and prevents wasting 5+ minutes "
                "on the wrong seed. Do NOT attempt to bypass this block.",
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
                "For a specific solution:\n"
                "  pwsh -NoProfile -File \"$HOME/.claude/scripts/Build-Solution.ps1\" -Solution \"SwyfftCI.slnx\"",
                file=sys.stderr,
            )
            sys.exit(2)

        # BLOCK: All test execution must go through Run-DotnetTest.ps1.
        # Scripts call it internally via pwsh -File, so "dotnet test" never appears
        # in their bash command. Raw "dotnet test" commands are always blocked.
        if re.search(r"dotnet\s+test|IntegrationTests\.exe|UnitTests\.exe", cmd) \
           and not re.search(r"# via-run-dotnet-test", cmd):
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
        if re.search(r"dotnet\s+test", cmd) and re.search(r"Excel\.IntegrationTests", cmd) \
           and not re.search(r'filter-trait\s+["\']?TestGroup=ByPerilTests', cmd) \
           and not re.search(r"ByPerilQuoteAuditDiagnosticTests", cmd):
            print(
                "BLOCKED: Excel integration tests must include --filter-trait \"TestGroup=ByPerilTests\" "
                "or target ByPerilQuoteAuditDiagnosticTests specifically. "
                "Running without this filter includes commercial tests which take an eternity. "
                "If you truly need all tests, ask the user to confirm.",
                file=sys.stderr,
            )
            sys.exit(2)

        # BELT-AND-SUSPENDERS: dotnet test must capture output with Tee-Object, --output Detailed, and --report-trx.
        if re.search(r"dotnet\s+test|IntegrationTests\.exe|UnitTests\.exe", cmd):
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
