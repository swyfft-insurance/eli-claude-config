# Meta: Rules Architecture

## When to read this file

Read this before modifying any rules file, CLAUDE.md, or memory.

## Architecture

- `~/.claude/CLAUDE.md` is a pointer file: the captain/crew preamble and a table pointing to rules files. Anything over two lines belongs in a rules file.
- `~/.claude/rules/*.md` hold the rules, one topic per file. Every rules file has a pointer row in CLAUDE.md.
- `~/.claude/plan-types/*.md` hold everything specific to one plan type, plus the rater playbooks both rater types read. Nothing loads them at launch: `plan-mode.md` Part A, a plan's pre-reads and `/eli--plan-audit` read the one a plan needs. `CLAUDE.md` has one pointer row for the folder. The one exception to "each rule lives in exactly one place": a type file writes out every rule its type depends on, so a rule that also governs work outside planning lives in its own file and in the type file. Every rule in a type file, bullet or numbered item, starts with a bold name, which `/eli--plan-audit` checks it by.
- `~/.claude/hooks/pretooluse.py` only blocks tool calls. A block message that carries rule text reads it from the rules file on disk. Never hardcode rule text in it.
- Each rule lives in exactly one place.

## Loading Priority Order

CLAUDE.md files load in this order, later meaning higher priority:

1. Managed (`/etc/claude-code/CLAUDE.md`)
2. User (`~/.claude/CLAUDE.md` + `~/.claude/rules/*.md`)
3. Project (`.claude/CLAUDE.md`, `.claude/rules/*.md`, from root to CWD)
4. Local (`CLAUDE.local.md` in each directory)

Personal behavioral rules live at the user level, project coding standards at the project level. Load order does not settle a conflict between a personal rule and a project rule. Raise every conflict with Eli, quoting both rules and recommending the personal one, and follow the personal rule until he rules. His ruling changes one side, and a repo-side change goes through its own PR. No conflict is left standing.

## Where to put a new rule

1. A correction in an existing category: edit the matching `~/.claude/rules/*.md` file.
2. A new category: create `~/.claude/rules/<topic>.md` and add its pointer row to CLAUDE.md.
3. A change to the Gates: edit `~/.claude/rules/core-behavior.md`.

## No "What happened" notes

Never write a "What happened" note, an account of the incident that prompted a rule, in a rules file, CLAUDE.md, a skill or memory. State the rule.

## Memory vs Rules

Memory (`~/.claude/projects/*/memory/`) holds only project-specific facts that can't be derived from code. Behavioral rules never go there. Memory constraints:

- The relevance scanner sees only filename, frontmatter description and type. Descriptions must be keyword-rich and specific, or the file is never recalled.
- 4,096-byte cap per memory file when surfaced per turn.
- At most 5 memory files injected per turn, 60KB per session.
- `autoDream` consolidates automatically after 24h or 5 sessions.

## Process for incorporating feedback

When Eli corrects your behavior: read this file, find the rules file the correction belongs in (or propose a new file and its pointer), draft the change and show him, and edit only after approval.
