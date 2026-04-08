# Seeding

- "seed elements local" → `Seed-Elements-Local.ps1` (elements only, ~45s)
- "seed database local" → `Seed-Database-Local.ps1` (full reseed, minutes)
- NOT interchangeable. Both build the solution. Seeder tracks file HASHES — clear `EFSeedingHistories` when only C# changed.
- Exit code 0 = seed completed. Trust it. Never re-run because you "didn't see all the logs."
