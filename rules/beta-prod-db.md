# Beta / Dev / Prod-Copy Database Access

## Data Availability
Investigate prod records (quotes, policies, prod failures) against prod-copy, which holds real prod data read-only. Use beta only when the subject is the beta environment itself (beta-only bugs, pre-release verification). Beta can also miss records. Prod is copied to beta every Monday, so beta has only records that existed before the most recent Monday. Never query beta as a shortcut because you can reach it and Eli has to run prod-copy: when the question needs prod data, hand Eli the prod-copy query.

## Scenario 1: Ad-hoc Queries Against Remote Databases
Follow `db-querying.md` § "Remote Database Queries". Never ask the user to run a query against prod itself; prod-copy is the target.

### Prod-Copy Database

| Property | Value |
|---|---|
| Server | `swyfftsqleastus2.database.windows.net` |
| Authentication | Microsoft Entra MFA |
| User | `eli.koslofsky@swyfft.com` |
| Encrypt | Mandatory (Trust Server Certificate) |
| Access | **read-only** |

### IMS Prod-Copy Database (on-prem)
IMS is on-prem SQL Server, and the Azure prod-copy has no IMS tables. Use `SwyfftImsStaging` (refreshed from prod every Monday) for any query mirroring prod IMS-reading code (storm exclusions, IMS claim lookups, `tblQuotes` / `tblClaims_Claim` / `tblClaimInformation` / `lstClaims_CatastropheCodes`). Prefer it over `SwyfftImsTest` on the same server, which has been out of sync.

| Property | Value |
|---|---|
| Server | `swyfftimstestdb.swyfft.com` |
| Authentication | Windows Authentication (Kerberos / AD) |
| Database | `SwyfftImsStaging` (Monday-refreshed prod copy) |
| Trust Server Certificate | Yes |
| Access | **read-only** in practice (refresh target, not the prod write source) |

**SSMS**: Server `swyfftimstestdb.swyfft.com`, Windows Authentication, Options → Connection Properties → Connect to database → `SwyfftImsStaging`, check Trust Server Certificate.

**sqlcmd** (Windows Authentication; VPN required; on Linux/WSL run `kinit eli.koslofsky@CORP.SWYFFT.COM` first):
```bash
sqlcmd -S swyfftimstestdb.swyfft.com -d SwyfftImsStaging -E -C -Q "SELECT ..."
```

## Scenario 2: Pointing Local Tests at Dev / Beta / Prod-Copy
All three environments are read-only, so any code path that writes to the DB fails.

### Environment reference

| Env | Deployment branch | Server | Core DB | Rating DB |
|---|---|---|---|---|
| Dev | `development` | `yde2xj08jm.database.windows.net,1433` | `SwyfftCoreDev` | `SwyfftRatingDev` |
| Beta | `beta` | `yde2xj08jm.database.windows.net,1433` | `SwyfftCoreBeta` | `SwyfftRatingBeta` |
| Prod-copy | `master` | `swyfftsqleastus2.database.windows.net` | `SwyfftCoreProd` | `SwyfftRatingProd` |

### Branch vs environment schema
Each environment's schema comes from its deployment branch (prod-copy carries `master`'s). Code from another branch fails once its migrations drift from the environment's schema: `IndexOutOfRangeException: <ColumnName>` from the generated `EF*_Generated.cs` mappers, `SqlException: Invalid column name` / `Invalid object name`, type-conversion errors, and others. On any schema-shaped error, check out the environment's deployment branch, rebuild, and re-run.

### Appsettings template
Edit `Swyfft.Common/appsettings.json`, replacing `SwyfftCore`, `SwyfftCoreSecondary`, `SwyfftRating` and `SwyfftRatingSecondary`:

```jsonc
"SwyfftCore":           "Data Source=<SERVER>;Initial Catalog=<CORE_DB>;Encrypt=True;App=Swyfft.Web;Max Pool Size=20000;Connection Timeout=60;Authentication=Active Directory Default;User ID=placeholder;",
"SwyfftCoreSecondary":  "Data Source=<SERVER>;Initial Catalog=<CORE_DB>;Encrypt=True;App=Swyfft.Console;Connection Timeout=60;Authentication=Active Directory Default;User ID=placeholder;",
"SwyfftRating":         "Data Source=<SERVER>;Initial Catalog=<RATING_DB>;Encrypt=True;App=Swyfft.Web;Max Pool Size=20000;Connection Timeout=60;Authentication=Active Directory Default;User ID=placeholder;",
"SwyfftRatingSecondary":"Data Source=<SERVER>;Initial Catalog=<RATING_DB>;Encrypt=True;App=Swyfft.Console;Connection Timeout=60;Authentication=Active Directory Default;User ID=placeholder;",
```

`User ID=placeholder` is a dummy that bypasses `CachedAzureAdAuthTokenRequirements` (otherwise: `Login failed for user ''`). `Authentication=Active Directory Default` uses the cached Azure AD token from Visual Studio or Azure CLI.

### Prerequisites
VPN connected, and Visual Studio signed in with Azure AD (or `az login`). When switching to the environment's branch (e.g., `git checkout beta`), do that first.

### Required env vars to run integration tests against beta/prod-copy
Set both in the test-run shell, with `az login` current:

```
$env:AZURE_TOKEN_CREDENTIALS = 'dev'   # so DefaultAzureCredential uses your az/VS token
$env:GITHUB_ACTIONS          = 'true'  # bypass the read-only TestGlobalIds write (see next section)
```

- Without `AZURE_TOKEN_CREDENTIALS=dev`, `DefaultAzureCredential` skips the Azure CLI / Visual Studio credentials and fails with `ManagedIdentityCredential authentication failed … IMDS … 169.254.169.254 … unreachable`. A valid `az account get-access-token` doesn't help without it. Check the token with `az account get-access-token --resource https://database.windows.net/ --query expiresOn -o tsv` (an error means `! az login`).
- `GITHUB_ACTIONS=true` skips the read-only counter write; see the next section.

### Read-only DB workaround (GITHUB_ACTIONS flag)
`Swyfft.Test.Base.GlobalPersistentCounter` writes to `dbo.TestGlobalIds` on every test-ID reservation, which fails on a read-only DB with `UPDATE permission was denied on the object 'TestGlobalIds'`. With `GITHUB_ACTIONS=true` it uses the in-memory `TestId.NewLinuxId()` path instead. The flag also changes `KeyVaultSecretsProvider` (skips local secrets) and `Log4NetConfigurator` (different logging config). If a test fails oddly with the flag set, suspect the flag first.

### When done
Revert `appsettings.json` to local defaults. Never commit connection string changes.
