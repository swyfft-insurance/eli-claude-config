# Domain Reference: Swyfft Codebase

## HomeownerStateConfig
- Declaration order has FUNCTIONAL SIGNIFICANCE — `GetAllValuesWithSortOrder()` uses reflection.
- `EnsureConfigOrderWithDatabase` test verifies declaration order matches DB order (by RenewalOn).
- When adding a new version: ALWAYS add at END of State/Carrier/RatingType group.
- Seeder overrides: new version's RenewalOn must be AFTER all previous versions.
  - **What happened:** NJ BSIC V8 override had RenewalOn before V7's → 426 test failures.

## Generator vs Config Versions
- Generator class version numbers (e.g., `DefaultElementGeneratorByPerilEAndSBenchmarkSpecialtyV6AL`) do NOT correspond to HomeownerStateConfig version numbers (e.g., `ALByPerilEAndSBenchmarkSpecialtyV6`). They are independent numbering schemes.
- Always check the factory mapping in `HomeownerDefaultElementGeneratorFactory.cs` to find which generator serves which config version.

## Comments and PR Descriptions
- Describe WHY and WHAT — not the debugging journey.
- Flag unexpected patterns: `SkipEachElementOptionTest = true`, disabled validation, skipped tests → STOP and ASK.

## Carrier Name Mappings
- Ark = Hadron (legacy name). Class named `Hsic` for FL/LA E&S.

## Branch-to-Environment Mapping

`development` → dev, `beta` → beta, `master` → **production**.

To determine when a PR deployed to prod, check when its commits arrived on `origin/master` (NOT the merge date of the feature PR into `development`):

```
git log origin/master --format="%h %ai %s" --ancestry-path <commit>^..origin/master | head -5
```

The first merge commit after `<commit>` on `origin/master` (typically a beta→master PR) is the approximate prod deploy timestamp. Don't say "deploy timing uncertain" — derive it.
