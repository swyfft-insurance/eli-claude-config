#!/usr/bin/env bash
# Prints a line for each Part of plan-mode.md that has no ## headings.
awk '/^# Part/{part=$0; n[part]=0; next} part && /^##/{n[part]++}
     END{for (p in n) if (n[p]==0) print "NO HEADINGS: plan-mode.md :: " p}' ~/.claude/rules/plan-mode.md
