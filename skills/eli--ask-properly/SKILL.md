# Ask Properly — replay my message with numbered choices

When invoked, do this and nothing else. No rule audits, no fact-check waves, no re-reading rules
files. The skill has exactly two jobs.

## Job 1: Re-present the last message with its questions formatted

Re-read the last message you sent before this skill was invoked. Output it again with its
information intact. The only change: every question or decision you put to Eli, including ones
buried in prose, multi-part asks and implicit "which way?" forks, moves into one list at the end,
formatted like this:

    1. <question>?
       1a. <option> (Recommended)
       1b. <option>

    2. <question>?
       2a. <option>
       2b. <option>

- Number each question. Letter each option, and prefix every option with its question number
  (`1a`, `1b`, `2a`), so Eli answers `1a, 2b` and nothing is ambiguous.
- Plain indented lines, never nested markdown bullets or code blocks inside an option. Anything
  Eli must read to decide (a commit message, a filename) goes in the question line, inline.
- Every option is a genuine choice. When you have a recommendation, it is option `a`, labeled
  "(Recommended)".
- Eli should never need more than a number plus a letter per question to answer.
- A question whose "yes" fires a gated write (GitHub, YouTrack, Slack, a git commit or push) is a
  plain yes/no question with no lettered options. The hook accepts only a bare "y" or "yes" for
  those, so lettered options hand Eli an answer the hook rejects.
- **`y/n` is only for a single gated write.** A question whose yes fires one GitHub, YouTrack,
  Slack, git commit or push call is a plain yes/no, because the hook accepts only a bare "y". Every
  other question gets numbered options, including design decisions, plan approval, rule changes and
  which findings to apply. A y/n on those asks Eli to approve something he cannot see the shape of.
- **One question per decision.** Independent items are separate questions, never one question whose
  options are subsets. A subset option hides which item Eli is ruling on, and it forces a package on
  him when he would have split it.
- **The question carries what is being decided.** Show the text, the name, or the line, before and
  after. A question that refers to a change without showing it can only be answered by scrolling
  back and reconstructing it.
- **Each option names the state it leaves behind.** Not the reasoning for it, and not a description
  of the change as an action. Options within a question are parallel: same shape, same level of
  detail, each readable on its own.

## Job 2: Ask the question you skipped

If your last message stopped without asking something Eli has to decide, that is the reason the
skill was invoked. The test: would you start working the moment Eli answered? If yes, it is a
question, and it goes in the list above, formatted the same way. Naming a blocker and stopping is
never an outcome of this skill.

When the choice is open-ended and you have no options yet, go find them first (read the code, run
the query), then present the real ones.

## Constraints

- Only reformat what you already asked, plus a question Job 2 requires. Never invent a decision
  neither of you faced.
- Don't answer the questions yourself, and don't start work until Eli answers.
- If the last message had no question and nothing is blocking you, say so in one line.
