# Beta/Dev Database Access

## Scenario 1: Ad-hoc Queries Against Remote Databases

1. ALWAYS draft and validate the query on localhost first
2. Present the validated query to the user
3. The user runs it against dev/beta/prod on your behalf
- Never connect directly to remote databases via sqlcmd
- ALWAYS use JOINs. Never ask user to run 2 separate queries. Never hardcode IDs across environments.

## Scenario 2: Pointing Local Tests at Dev/Beta

When running local code/tests against dev/beta Azure SQL:
1. Edit `Swyfft.Common/appsettings.json` connection strings:
   - Server: `yde2xj08jm.database.windows.net,1433`
   - Beta: `SwyfftCoreBeta` / `SwyfftRatingBeta`; Dev: `SwyfftCoreDev` / `SwyfftRatingDev`
   - Must include: `Authentication=Active Directory Default` + `User ID=placeholder`
   - `User ID=placeholder` is a dummy value — satisfies the connection string parser, not a real credential. Bypasses `CachedAzureAdAuthTokenRequirements` (otherwise: `Login failed for user ''`)
2. May also checkout the matching branch (`git checkout beta`) depending on the scenario
3. Requires VPN + Visual Studio signed in with Azure AD
4. REVERT when done. Don't commit connection string changes.
