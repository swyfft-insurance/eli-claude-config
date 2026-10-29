# Compaction

## The resume file

Work after a compaction resumes from one file on disk, never from the summary.

- The resume file is the plan. Its pre-reads list every mandatory read (rules files, skills, repo docs), and its Progress section shows where the work stands. With no plan yet, it is `resume.md` in the ticket folder: the mandatory reads, every decision in Eli's words, the open questions, and what is done and outstanding.

## Before Eli compacts

- Before Eli compacts, `/eli--prep-for-compact` brings the resume file current and hands him the command:

  ```
  /compact Read <the plan, or resume.md when there's no plan> in its entirety, then every mandatory read it lists. Then tell me the next step, and wait for my go-ahead before starting it.
  ```

## After the compaction

- After the compaction, those reads come first. The summary and the rules loaded at session start don't count as having read them.
