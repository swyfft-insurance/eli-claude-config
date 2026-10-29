# Plan type: LogMonitor bug

## 1. What makes it a LogMonitor bug

- **A ticket filed from a production error signature.** Supersedes Bug. Audit-doc LogMonitor supersedes it: an audit-doc ticket is planned as Audit-doc LogMonitor, never as this.

## 2. Requirement

- **Its scope is every occurrence of that signature.**

## 3. Discovery

Follows `bug.md`, plus:

- **Every log search goes through `/search-logs`,** never the repo's `solarwinds` skill, `fix-log-bug` or `swo`.
- **Run a ticket's SolarWinds query verbatim:** URL-decode it and run every term and scope exactly, including the full `program:(...)` list and the severity. Never paraphrase, narrow or substitute terms. Zero results from a modified query prove nothing. Propose a different query only after running the verbatim one, labeled as not the ticket's query.

## 4. Design

- **The repo's `AGENTS.md` § "Logging" governs every logging change.** Its pointer to the `fix-log-bug` skill's Silencing Check is not followed.

## 5. Steps and stops

- **The Bug sequence (`bug.md`).**
