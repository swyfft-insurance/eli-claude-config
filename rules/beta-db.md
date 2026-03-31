# Beta/Dev Database Testing

When pointing local tests at beta/dev Azure SQL:
1. Checkout branch matching target environment (`git checkout beta`)
2. Edit `Swyfft.Common/appsettings.json` connection strings:
   - Server: `yde2xj08jm.database.windows.net,1433`
   - Beta: `SwyfftCoreBeta` / `SwyfftRatingBeta`; Dev: `SwyfftCoreDev` / `SwyfftRatingDev`
   - Must include: `Authentication=Active Directory Default` + `User ID=placeholder`
   - `User ID=placeholder` is a dummy value — it satisfies the connection string parser, not a real credential. Bypasses `CachedAzureAdAuthTokenRequirements` (otherwise: `Login failed for user ''`)
3. Requires VPN + Visual Studio signed in with Azure AD
4. REVERT when done. Don't commit connection string changes.
