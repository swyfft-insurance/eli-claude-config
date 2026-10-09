#!/usr/bin/env bash
# Prints the code-complete audit's governing rule files, one per line, in wave order.
repoRoot="$(git rev-parse --show-toplevel)"
printf '%s\n' \
  ~/.claude/rules/coding-standards.md \
  ~/.claude/rules/comments-docs-and-external-writing.md \
  ~/.claude/rules/testing.md \
  ~/.claude/rules/refactoring.md \
  ~/.claude/rules/swyfft-domain.md \
  "$repoRoot/AGENTS.md"
for f in "$repoRoot"/.claude/rules/*.md; do
  case "$(basename "$f")" in
    frontend-*|powershell.md|teamcity.md|openapi-spec.md) ;;
    *) printf '%s\n' "$f" ;;
  esac
done
