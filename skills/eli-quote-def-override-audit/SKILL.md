---
name: eli-quote-def-override-audit
description: Audit the quote-def overrides (Homeowner Seeder.cs + Flood/DBB EnvironmentFilters) and list the ones whose configs have already gone live in prod — stale overrides that are removal candidates. Use when deciding which overrides to clean up, or as a periodic hygiene check. Report-only — it never edits Seeder.cs / EnvironmentFilters.
---

# Quote-Def Override Audit

Runs the `ReportStaleOverridesForLiveConfigs` audit in `QuoteDefinitionsUnitTests`
(`Swyfft.Services.UnitTests`). It lists every quote-def override whose config has **already gone live
in prod** — its real `QuoteDefinitions.txt` `NewQuotesOn` is in the past, so the override's only
purpose (let dev/beta test the config *before* go-live) is spent and it's a **removal candidate**.
Overrides whose config isn't live yet, or that have no prod row at all (the override is the config's
only activation), are left alone.

Covers Homeowner (`Seeder.LocalAndDevAndBeta...` + `LocalAndDev...`), Flood, and DBB
(`EnvironmentFilters.FloodOverrides` / `DbbOverrides`). Threshold for "live" is prod
`NewQuotesOn < DateTime.UtcNow`.

## Why a test, not a script

The override entry already *is* its quote-def key — in C# the override's config resolves straight to
its `QuoteDefinitions.txt` row (`StateConfigName`). A text-parsing script would have to rebuild that
symbol→key mapping from the closed-set classes (fragile). The audit lives in `QuoteDefinitionsUnitTests`
and reuses its loaders + override arrays, getting the mapping for free. It's gated on an env var, so
the run skips it in normal/CI test flows.

## Arguments

None — it audits the whole override set.

## Run

```
pwsh -NoProfile -File "$HOME/.claude/scripts/Run-QuoteDefOverrideAudit.ps1"
```

Pass `-NoBuild` if the solution is already built. No DB, no appsettings changes — pure unit test
over static files.

## After the Run

1. The audit result is in the run's stdout — no need to open the TEMP log. If any overrides are stale
   the test fails, listing each one (config + the prod date it went live). A clean pass means none —
   nothing to remove.
2. Present the list to the user — it's the authoritative, deterministic set of removal candidates.
   Don't hand-check it.

**This skill audits only.** Removing the listed overrides is a separate decision the user makes — do
NOT edit `Seeder.cs` / `EnvironmentFilters.cs` as part of running the audit.
