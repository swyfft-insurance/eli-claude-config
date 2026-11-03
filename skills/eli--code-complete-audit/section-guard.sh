#!/usr/bin/env bash
# Prints every rule section the latest audit run has no row for. Usage, from the repo root: section-guard.sh <ticket-folder>
# Kept out of SKILL.md: the skill loader replaces a dollar sign followed by 0 there with the skill's arguments.
audit=~/.claude/tickets/"$1"/artifacts/code-complete-audit.md
run="$(awk '/^## Run /{run=""} {run=run $0 "\n"} END{printf "%s", run}' "$audit")"
bash ~/.claude/skills/eli--code-complete-audit/audit-files.sh | while IFS= read -r f; do
  name="$(basename "$f")"
  grep -qF -- "$name :: no file in the diff matches its paths" <<<"$run" && continue
  grep -q '^## ' "$f" || echo "NO SECTIONS: $name"
  grep '^## ' "$f" | sed 's/^## //' | while IFS= read -r heading; do
    grep -qF -- "$name :: $heading" <<<"$run" || echo "MISSING: $name :: $heading"
  done
done
