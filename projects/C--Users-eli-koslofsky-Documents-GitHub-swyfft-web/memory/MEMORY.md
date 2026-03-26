# Swyfft Web — Memory Index

## !!!!! THE THREE RULES — READ `core-rules.md` EVERY SESSION !!!!!

1. **VERIFY before claiming.** Never state unverified guesses as facts.
2. **ASK before acting.** Never add scope, make destructive changes, or post externally without approval.
3. **STOP when told to stop.** Zero tool calls. Words only.

These exist because Claude has violated all three repeatedly, causing real professional damage.
**If you remember nothing else, remember these.**

## Topic Files

| File | What's In It |
|------|-------------|
| `core-rules.md` | **START HERE.** Behavioral rules, draft-before-posting workflow, verification workflow |
| `dotnet-testing.md` | Test listing, trait filters, ByPeril Excel tests, tee output, no --no-build |
| `tooling-gotchas.md` | sqlcmd, SQL queries, sed, Slack formatting, GitHub PR threads, git branches, seeding, rater diffs |
| `codebase-patterns.md` | HomeownerStateConfig ordering, comment style, flagging unexpected patterns |
| `pr-creation.md` | PR creation rules — never guess tickets, always read YouTrack + diff |
| `manual-testing.md` | How to prompt for manual QA — specific data, one action per prompt |
| `feedback_no_logical_commits.md` | Never use /logical-commits unless explicitly asked |
| `feedback_slack_no_duplicate_msgs.md` | Delete/edit wrong Slack messages before resending — never duplicate |
| `feedback_pr_descriptions.md` | Verify all PR claims against reality; skip review guides for iterative commits |
| `feedback_show_means_show.md` | PRINT code in response text when asked to show — tool output is invisible to user |
| `feedback_questions_not_instructions.md` | Questions about code are DISCUSSIONS — explain, don't change. Wait for explicit instruction. |
| `feedback_plans_read_memory_first.md` | ALWAYS read memory before ANY external action or multi-step task — not just plans |
| `feedback_fix_access_not_functionality.md` | Fix access modifiers (private→protected) instead of rewriting logic to avoid the call |
| `feedback_no_tail_background.md` | Never pipe background commands through tail/head — buffers all output, hides progress |
| `feedback_resolve_all_pr_threads.md` | Always resolve ALL PR threads after replying — merge requires it |
| `feedback_pr_comment_workflow.md` | PR comment replies need draft-approve cycle too — read memory first, draft first, resolve all |
| `feedback_safe_file_moves.md` | Never use mv — cp then verify then rm. Lost untracked file to silent mv failure on Windows |
| `feedback_no_embellish_actions.md` | Do exactly what's asked — no unsolicited comments/messages on external actions |
| `feedback_no_lazy_global_usings.md` | Never add global usings as a shortcut — add usings to each file individually |
| `feedback_never_mix_merge_commits.md` | Merge commits ONLY contain conflict resolution — never mix with PR feedback or fixes |
| `feedback_pr_review_style.md` | Only comment on fundamental bugs/red flags — no nits, no style comments |
| `feedback_no_noop.md` | Never use "no-op" — always find a plain English alternative |
| `feedback_fetch_before_branch_claims.md` | Always git fetch before claiming what's on remote branches — stale locals cause wrong theories |
| `feedback_no_premature_exitplan.md` | Do not call ExitPlanMode while actively discussing the plan — wait for conversation to conclude |
| `feedback_youtrack_no_drafts.md` | Always use create_issue, never create_draft_issue — avoids duplicates |
| `feedback_youtrack_read_all_fields.md` | Always read and call out ALL custom fields (Carrier, State, ProductLine, etc.) — they scope the work |
| `feedback_bot_reviews.md` | Treat bot PR comments (Copilot, Claude) with same seriousness as human comments |
| `feedback_exclude_not_revert.md` | "Commit minus X" means don't stage X — never revert/checkout those files |
| `feedback_wait_for_user_input.md` | When AskUserQuestion rejected with "clarify" + no answer, user is typing — WAIT |
| `feedback_read_tickets_first.md` | Read YouTrack tickets FIRST before exploring code — error msgs have the root cause |
| `feedback_prebind_captured_assert_tests.md` | "Run pre-bind captured assert tests" = 3 projects with trait filter, build first |
| `feedback_read_docs_before_running.md` | Read CLAUDE.md docs BEFORE running console tasks — never guess parameters |
| `reference_beta_db_connection.md` | How to point local tests at beta/dev Azure SQL DBs |
| `feedback_no_bash_tee.md` | bash tee crashes on Windows — use pwsh Tee-Object with Windows paths |

## Active Work

| File | Notes |
|------|-------|
| `sw47057-progress.md` | **ACTIVE** SW-47057 fix for RawSarHurricanePremium crash. Implementation done, tests need real prod data. |

