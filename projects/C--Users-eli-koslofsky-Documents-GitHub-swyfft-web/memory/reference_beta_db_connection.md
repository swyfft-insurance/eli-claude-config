---
name: Pointing local tests at beta/dev Azure SQL DBs
description: How to run integration tests against beta or dev databases instead of localhost
type: reference
---

## Pointing Local Tests at Beta/Dev DBs

When you need to run tests against real beta/dev data (e.g., reproducing a prod bug with real quote data):

### Prerequisites
- Must be on VPN
- Must have Visual Studio signed in with your Swyfft Azure AD account

### Steps

1. **Checkout the branch matching the target environment** (e.g., `git checkout beta`). The local code schema must match the target DB schema or you'll get column mismatch errors like `IndexOutOfRangeException: CensusBlock2010`.

2. **Edit `Swyfft.Common/appsettings.json`** — change `SwyfftCore` and `SwyfftRating` connection strings:
   ```
   "SwyfftCore": "Data Source=yde2xj08jm.database.windows.net,1433;Initial Catalog=SwyfftCoreBeta;Encrypt=True;Authentication=Active Directory Default;App=Swyfft_Beta;Connection Timeout=60;Max Pool Size=20000;User ID=placeholder;",
   "SwyfftRating": "Data Source=yde2xj08jm.database.windows.net,1433;Initial Catalog=SwyfftRatingBeta;Encrypt=True;Authentication=Active Directory Default;App=Swyfft_Beta;Connection Timeout=60;Max Pool Size=20000;User ID=placeholder;",
   ```
   For dev, use `SwyfftCoreDev` / `SwyfftRatingDev` instead.

3. **Key details:**
   - `Authentication=Active Directory Default` tells SqlClient to use `DefaultAzureCredential` (picks up VS credentials)
   - `User ID=placeholder` is required to bypass `CachedAzureAdAuthTokenRequirements`, which otherwise detects Azure SQL + no credentials and tries to set `AccessToken` via `IAzureAdAuthService` (which is faked in tests)
   - Without both of these, you get `Login failed for user ''`

4. **Revert when done** — restore the connection strings to localhost. Don't commit these changes.

### Beta connection strings (from `appsettings.Beta.json`)
- Core: `SwyfftCoreBeta` on `yde2xj08jm.database.windows.net`
- Rating: `SwyfftRatingBeta` on `yde2xj08jm.database.windows.net`

### Dev connection strings (from `appsettings.Development.json`)
- Core: `SwyfftCoreDev` on `yde2xj08jm.database.windows.net`
- Rating: `SwyfftRatingDev` on `yde2xj08jm.database.windows.net`
