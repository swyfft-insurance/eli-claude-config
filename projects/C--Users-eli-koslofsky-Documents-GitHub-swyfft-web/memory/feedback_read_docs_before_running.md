---
name: Read docs before running console tasks
description: ALWAYS read CLAUDE.md docs for console tasks (ReadExcel, DumpRater, etc.) before running them — never guess parameters
type: feedback
---

ALWAYS read the relevant CLAUDE.md documentation BEFORE running any console task (ReadExcel, DumpRater, ReadNamedRanges, etc.). Never guess parameters or flags.

**Why:** Wasted 10+ minutes running DumpRater with wrong parameters (missing -o flag, wrong -sheet name) because I didn't read the docs first. The tasks are thoroughly documented in `Swyfft.Seeding/ExcelLoaders/ByPeril/CLAUDE.md` and `Swyfft.Services.Excel.IntegrationTests/CLAUDE.md`.

**How to apply:**
- Before running ANY console task, read the relevant CLAUDE.md for usage examples
- `ReadExcel` = interactive, outputs to console, good for quick inspection. No `-o` needed.
- `DumpRater` = full dump to file, requires `-o:"path"`. Good for diffing.
- `ReadNamedRanges` = lists named ranges, supports `-RegexFilter`
