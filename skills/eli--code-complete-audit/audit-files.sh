#!/usr/bin/env bash
# Prints the code-complete audit's governing rule files, one per line, in pass order.
repoRoot="$(git rev-parse --show-toplevel)"
for f in ~/.claude/rules/*.md; do
  awk 'NR==1&&/^---/{fm=1;next} fm&&/^---/{exit} fm&&/^audited-by:/' "$f" | grep -q 'code-complete' \
    && printf '%s\n' "$f"
done
printf '%s\n' "$repoRoot/AGENTS.md"
for f in "$repoRoot"/.claude/rules/*.md; do
  case "$(basename "$f")" in
    frontend-*|powershell.md|teamcity.md|openapi-spec.md) ;;
    *) printf '%s\n' "$f" ;;
  esac
done
