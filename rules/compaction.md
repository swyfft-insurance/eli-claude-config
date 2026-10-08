# Compaction

Work after a compaction resumes from one file on disk, never from the summary.

- **The resume file is the plan.** Its pre-reads list every mandatory read: the rules files, the
  skills in force and the repo docs. Its Progress section shows where the work stands. With no plan
  yet, the resume file is `resume.md` in the ticket folder, doing the same job: the mandatory reads,
  every decision in Eli's words, the open questions, and what is done and what is outstanding.
- **Before Eli compacts,** `/eli--prep-for-compact` makes the resume file complete and current, then
  hands him the command.
- **The command:**

  ```
  /compact Read <the plan, or resume.md when there's no plan> in its entirety, then every mandatory read it lists. Then tell me the next step, and wait for my go-ahead before starting it.
  ```

- **After the compaction, those reads come first.** The summary and the session-start rules injection
  don't count as having read them.
