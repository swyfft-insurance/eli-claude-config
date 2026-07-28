# Beta / Dev / Prod-Copy Database Access

## Data Availability

Prod data is copied to beta **every Monday**. Any prod record (quote IDs, policy numbers, element states) that existed before the most recent Monday copy is in beta. Don't plan workarounds to extract prod data manually when the record predates last Monday — just point appsettings at beta.

## Scenario 1: Ad-hoc Queries Against Remote Databases

1. Follow the query construction rules in `db-querying.md` (validate on localhost, use JOINs, no hardcoded IDs)
2. Present the validated query to the user
3. The user runs it against dev/beta/prod-copy on your behalf
- Never connect directly to remote databases via sqlcmd

### Prod-Copy Database

| Property | Value |
|---|---|
| Server | `swyfftsqleastus2.database.windows.net` |
| Authentication | Microsoft Entra MFA |
| User | `eli.koslofsky@swyfft.com` |
| Encrypt | Mandatory (Trust Server Certificate) |
| Access | **read-only** |

Prefer prod-copy over beta when the query needs *real* prod data and beta might not have it:
- Record was created in the current week (beta is a weekly Monday snapshot)
- Record is expected in beta but missing (beta-copy anomaly)
- Verifying a prod-vs-beta discrepancy

Never ask the user to run a query against prod directly — Eli has no write access, and the prod-db hook blocks it anyway. Prod-copy is the right target.

### IMS Prod-Copy Database (on-prem)

IMS is on-prem SQL Server, not Azure. The weekly Monday refresh from prod populates `SwyfftImsStaging`, which serves as the prod-copy. Use it for any query mirroring prod IMS-reading code (storm exclusions, IMS claim lookups, `tblQuotes` / `tblClaims_Claim` / `tblClaimInformation` / `lstClaims_CatastropheCodes`). The Azure Core/Rating prod-copy doesn't have IMS tables.

| Property | Value |
|---|---|
| Server | `swyfftimstestdb.swyfft.com` |
| Authentication | Windows Authentication (Kerberos / AD) |
| Database | `SwyfftImsStaging` (Monday-refreshed prod copy) |
| Trust Server Certificate | Yes |
| Access | **read-only** in practice (refresh target, not the prod write source) |

`SwyfftImsTest` exists on the same server but has been flagged out-of-sync historically — prefer `SwyfftImsStaging`.

**SSMS**: Server `swyfftimstestdb.swyfft.com`, Windows Authentication, Options → Connection Properties → Connect to database → `SwyfftImsStaging`, check Trust Server Certificate.

**sqlcmd (Linux/WSL — needs Kerberos ticket first)**:
```bash
kinit eli.koslofsky@CORP.SWYFFT.COM   # VPN required
sqlcmd -S swyfftimstestdb.swyfft.com -d SwyfftImsStaging -E -C
```

## Scenario 2: Pointing Local Tests at Dev / Beta / Prod-Copy

All three environments are **read-only** — any code path that writes to the DB will fail. That's a safety net, not a bug. Use it.

### Environment reference

| Env | Deployment branch | Server | Core DB | Rating DB |
|---|---|---|---|---|
| Dev | `development` | `yde2xj08jm.database.windows.net,1433` | `SwyfftCoreDev` | `SwyfftRatingDev` |
| Beta | `beta` | `yde2xj08jm.database.windows.net,1433` | `SwyfftCoreBeta` | `SwyfftRatingBeta` |
| Prod-copy | `master` | `swyfftsqleastus2.database.windows.net` | `SwyfftCoreProd` | `SwyfftRatingProd` |

### Branch vs environment schema

Each environment's schema is migrated by its deployment branch (table above; prod-copy carries prod's schema, so `master`'s). Code from a different branch runs fine against the environment until the branch's migrations are out of sync with the environment's schema. Migration drift can surface as a whole assortment of schema-mismatch failures anywhere an entity is queried or mapped — `IndexOutOfRangeException: <ColumnName>` (the generated `EF*_Generated.cs` mappers read result-set columns by name), `SqlException: Invalid column name` / `Invalid object name` (a column or table named in the SQL doesn't exist in the environment), type-conversion errors on a changed column, among others. When a run against a remote environment fails with any schema-shaped error, the fix is to check out the environment's deployment branch, rebuild, and re-run.
  - **What happened:** `development` code against `SwyfftCoreBeta` threw `IndexOutOfRangeException: OfacMatchStatus` — a `development` migration beta didn't have yet.

Prefer prod-copy over beta when the query needs *real* prod data (see Scenario 1 for when).

### Appsettings template

Edit `Swyfft.Common/appsettings.json`. Replace `SwyfftCore`, `SwyfftCoreSecondary`, `SwyfftRating`, `SwyfftRatingSecondary`:

```jsonc
"SwyfftCore":           "Data Source=<SERVER>;Initial Catalog=<CORE_DB>;Encrypt=True;App=Swyfft.Web;Max Pool Size=20000;Connection Timeout=60;Authentication=Active Directory Default;User ID=placeholder;",
"SwyfftCoreSecondary":  "Data Source=<SERVER>;Initial Catalog=<CORE_DB>;Encrypt=True;App=Swyfft.Console;Connection Timeout=60;Authentication=Active Directory Default;User ID=placeholder;",
"SwyfftRating":         "Data Source=<SERVER>;Initial Catalog=<RATING_DB>;Encrypt=True;App=Swyfft.Web;Max Pool Size=20000;Connection Timeout=60;Authentication=Active Directory Default;User ID=placeholder;",
"SwyfftRatingSecondary":"Data Source=<SERVER>;Initial Catalog=<RATING_DB>;Encrypt=True;App=Swyfft.Console;Connection Timeout=60;Authentication=Active Directory Default;User ID=placeholder;",
```

- `User ID=placeholder` is a dummy value — satisfies the connection string parser. Bypasses `CachedAzureAdAuthTokenRequirements` (otherwise: `Login failed for user ''`)
- `Authentication=Active Directory Default` picks up the cached Azure AD token from Visual Studio / Azure CLI — no MFA prompt if you're already signed in.

### Prerequisites

- VPN connected
- Visual Studio signed in with Azure AD (or `az login`)
- If switching branches to match env (e.g., `git checkout beta`), do that too

### Required env vars to run integration tests against beta/prod-copy (don't waste time on this again)

Set BOTH in the test-run shell, and `az login` must be current:

```
$env:AZURE_TOKEN_CREDENTIALS = 'dev'   # so DefaultAzureCredential uses your az/VS token
$env:GITHUB_ACTIONS          = 'true'  # bypass the read-only TestGlobalIds write (see next section)
```

- **`AZURE_TOKEN_CREDENTIALS=dev` is mandatory.** The connections use `Authentication=Active Directory Default` → `DefaultAzureCredential`. Without this var the in-process chain skips the dev credentials (Azure CLI / Visual Studio) and falls through to `ManagedIdentityCredential` (Azure-VM-only), failing with `ManagedIdentityCredential authentication failed … IMDS … 169.254.169.254 … unreachable`. Setting it to `dev` restricts the chain to dev creds, so it uses your `az login` token.
- **A passing `az account get-access-token` is necessary but NOT sufficient** — the token can be valid yet unused without `AZURE_TOKEN_CREDENTIALS=dev`. Verify the token exists with `az account get-access-token --resource https://database.windows.net/ --query expiresOn -o tsv` (future timestamp = good; error → `! az login`), then still set the var.
- **`GITHUB_ACTIONS=true`** — bypasses the read-only counter write; see the next section.

### Read-only DB workaround (GITHUB_ACTIONS flag)

`Swyfft.Test.Base.GlobalPersistentCounter` writes to `dbo.TestGlobalIds` on every test-ID reservation. Against a read-only DB (like prod-copy), this fails with `UPDATE permission was denied on the object 'TestGlobalIds'` before the actual test runs.

Bypass: set `GITHUB_ACTIONS=true` in the test-run shell. `GlobalPersistentCounter` switches to the Linux code path (`TestId.NewLinuxId()`) — pure in-memory `Interlocked.Increment`, no SQL.

**Caveats** — other code paths also check `IsGithubActions()`:
- `KeyVaultSecretsProvider` — alters the secrets-loading code path (skips local secrets).
- `Log4NetConfigurator` — uses a different logging config.

For audit-mismatch reproduction tests these haven't caused issues, but if a test fails in a weird way while this flag is set, suspect the flag first.

### When done

REVERT `appsettings.json` to local defaults. Don't commit connection string changes.
