# Quote-def Dates: real vs override, and what gets seeded

Every quote def has two independent date pairs (`NewQuotesOn`, `RenewalOn`):

- **Real / prod**: in `QuoteDefinitions.txt`. The production go-live; governs prod.
- **Override**: in `Seeder.cs` → `CustomizeCoreLocalAndDevAndBeta`. Local/dev/beta only; lets you
  test a config before its prod go-live.

New configs often sit at a parked far-future placeholder date until go-live is known; **activating**
= swapping that placeholder for the real date.

**Seeded DB (local/dev/beta)** = the override if the config has one, else its `QuoteDefinitions.txt`
date. The override replaces the real date at seed time. Prod has no overrides, so prod = real dates.

**Activating does not remove the override.** It only changes the `QuoteDefinitions.txt` date. The
override stays and keeps governing the seeded date, so read `Seeder.cs` for a config's effective
date; don't assume the real one.

**A test sees** the override (effective) date if it reads the seeded DB, or the real date if it reads
`QuoteDefinitions.txt` / configs in-memory.

Ordering tests that consume these dates: `Swyfft.Services/Common/Homeowner/CLAUDE.md` §§
"QuoteDefinitions.txt Ordering" and "Seeder Override RenewalOn Must Be Monotonically Increasing".

## Finding stale overrides: the `/eli--quote-def-override-audit` skill

Once a config's real prod `NewQuotesOn` is in the past, its override has done its job (early
dev/beta testing before go-live) and is a removal candidate. Don't hand-compare the override array
against `QuoteDefinitions.txt` to find these. Run `/eli--quote-def-override-audit`. It deterministically
lists every HO/Flood/DBB override whose config is already live in prod (the removal candidates),
leaving alone the ones not yet live or with no prod row. Report-only; deciding to remove is a
separate step.
