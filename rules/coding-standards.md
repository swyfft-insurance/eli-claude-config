# Coding Standards

## SOLID governs the design

New code conforms from the start.

Existing code gets refactored toward SOLID when it is already in scope and the refactor stays
small. A rename, an extracted method, a narrowed interface: do it as part of the change.

When the fix would push well past what the ticket asked for, stop. Name the violation, say what the
fix would involve, and ask how much of the fix belongs in the pull request, user story, or bug being
worked on, if any. That call is Eli's.

## Identifier names must be self-documenting

<!-- Added 2026-09-02 after SW-53770 Part 4 — Eli correction on GetGroupRadix and other generic names -->

Applies to identifiers in code: variable, property, method, parameter, field, constant, and type
names. Not file, branch, or ticket naming.

An identifier says what the thing is used for. Prefer verbosity over brevity. A generic name that
leaves a reader asking "for what?" is the failure: `GetGroupRadix` names neither which group nor
what the radix is for, where `GetElementCombinationPermutationCount` names both.

Abbreviation is fine as long as the name still reads and still says what the thing is for —
`CalcEachElementOptIterCount` is acceptable. What is not acceptable is a name that is short because
the meaning was left out.

The test: read the identifier at a use site with nothing else on screen. If it does not say what
the thing holds or returns and what it is for, it is too short.

## General

- **We own this code. Its current shape is not a constraint on the solution.** Access modifiers, method signatures, where a value is computed, how a class is split: all of it is ours to change as part of the work. If the clean approach needs a `private` member made `protected`, a signature widened, or logic moved, change it; never contort the approach to avoid touching existing code. "It's written this way now" is not a reason. The only real constraints are external (public API contracts, on-disk/DB formats, regulatory rules), and even those change with the right migration. (Most common instance: fix `private` → `protected` instead of rewriting logic to dodge the call. Never treat access modifiers as immutable.)
- Never add global usings as a shortcut. Add `using` to each file individually.
- Prefer collection expressions (`[a, b, c]`, `[.. source]`) over `new()`, `new T[] {}`, `new List<T> {}`, and `.ToList()`/`.ToArray()` wherever the target type supports them, including `TheoryData<T>`. This is the default for collection initialization and construction.
- Prefer `.ToTheoryData()` to build `TheoryData<T>` from an existing sequence/query rather than hand-rolling `new TheoryData<T>()` + `.Add(...)` in a loop. (For a hand-written literal set of rows, a collection expression `[...]` is fine.)

## Line Length

C# code lines must stay at or below **120 characters** including leading indent. This is a hard rule — wrap longer lines at natural punctuation: after commas, before operators, between method-chain links, or after the opening paren of a method call. Applies to `.cs` files only (production code AND tests). Markdown, `.txt` data files, JSON, YAML, etc. are exempt — prose and config wrap differently than code. No exceptions for "readability" within `.cs` — if the line is over, it gets wrapped.

When a wrapped construct has multiple peer items (e.g., theory data rows, parameter lists, collection initializers), pick ONE wrapping pattern and apply it to ALL peers — don't mix single-line and multi-line entries in the same group. Inconsistent wrapping is the worst of both worlds and will be flagged.

This applies only to lines newly written or modified by the current change. Pre-existing long lines that aren't being touched stay as-is — don't hijack the diff to reformat unrelated code.

**Verification**: `~/.claude/scripts/Test-LineLength.ps1 -Mode local` (or `-Mode branch`) scans the unified diff for added/modified `.cs` lines and exits non-zero if any exceed 120 chars. `~/.claude/scripts/Build-Solution.ps1` runs this as a pre-build gate (and aborts the build on failure), so a plan that already builds does NOT need a separate line-length verification step — call it out standalone only when the plan doesn't build (e.g. markdown-only changes) or as a pre-build self-check. The script is a backstop, not a substitute for writing it correctly the first time — self-check while editing rather than relying on the post-hoc gate.

<!-- Added 2026-09-02 during SW-55797 — Eli: formatting was allowed to reopen an approved code
     decision, and the conflict was presented to him as a blocker to adjudicate -->

**Line length never dictates code shape.** The 120-character limit is presentation. The code's
structure is the substance, and the two are never traded against each other. When a change makes a
line too long, wrap the line. Never restructure working code, never split or merge a method, never
alter an approved design, and never reopen a settled decision to make lines fit. C# wraps at any
token, so a legal wrapping always exists.

This covers a line that only moves. Re-indenting an over-length line makes it a modified line, so
it gets wrapped in the same edit. That is mechanical work, not a finding.

A line-length violation is therefore never a blocker, never a HARD STOP, and never an option put to
Eli. Presenting one that way is a fake blocker. It halts delivery over whitespace and asks Eli to
adjudicate formatting.

- **What happened:** nesting a switch re-indented two already-long lines. That was raised as a
  blocker, with a restructure of the approved code offered as the way around it.

## Magic Numbers / Strings

Hardcoded numeric / string literals must be extracted to named constants. Even sentinels like `int.MaxValue` used to mean "no limit" get a named alias — the name encodes intent the value alone doesn't. Applies to plan code excerpts AND executed code.

Bad: `RenderSheet(ws, int.MaxValue, 64, lines.Add);`

Good:
```csharp
const int allRows = int.MaxValue;
const int maxColumnsToCapture = 64;
RenderSheet(ws, allRows, maxColumnsToCapture, lines.Add);
```

**Scope a constant to its only user.** A constant read by one method is a `const` declared at the
start of that method, never a field or property on the class. It moves to the class only once a
second member needs it. Local constants are camelCase: `const double metersPerKilometer = 1_000D;`.
A value that can't be `const`, such as an array, goes in the same place as a local.

- **What happened:** SW-53906's address selector declared `MetersPerKilometer`, `MissingCoordinate`
  and a distance sentinel on the class, each read by a single method.

## ClosedSets

ClosedSets are pervasive in this codebase and carry strict usage rules — parameter typing,
comparisons, `.Value`, `.ToString()`, `.Switch()`, implicit string conversion, and
ModelBinder/JsonConverter at boundaries — all defined in `Swyfft.Common/SetDefinitions/CLAUDE.md`.
Reviewers (human and bot) reject PRs for violating them.

**Mandatory read before writing ClosedSet code.** Before you write or modify any C# that touches a
ClosedSet — typing a parameter, comparing values, calling `.Value`/`.ToString()`/`.Switch()`, or
crossing a UI/API boundary — read `Swyfft.Common/SetDefinitions/CLAUDE.md` in full. Don't work from
memory: having read it earlier in the session — even having *edited* it — does NOT keep its rules
active while you later write unrelated code.

**Mandatory ClosedSet self-audit at code-complete.** Before the code-complete HARD
STOP, re-read `Swyfft.Common/SetDefinitions/CLAUDE.md` (don't work from memory) and audit every
ClosedSet usage the diff adds or changes against it. Confirm in particular: new method parameters
are typed as the ClosedSet, not `string`/`int`; `.Value` appears only at true system boundaries
(external APIs, IMS, raw storage), never in internal calls that already accept the ClosedSet;
comparisons and `.Switch()` follow the documented forms. Fix every violation before announcing
code-complete. This audit is part of reaching code-complete — not a step the user should ever have to request.

## Dispatch dictionaries: behavior keyed by a value

When behavior varies by a key and only some keys behave specially, declare it as a dispatch
dictionary: an `IReadOnlyDictionary` from the key to a function, backed by a plain `Dictionary`,
with one entry per key that behaves differently. Callers look up with `TryGetValue`, and a key
with no entry takes the default behavior.

```csharp
private static IReadOnlyDictionary<County, Func<EFHomeownerQuote, decimal>> NamedStormMinimumByCounty { get; } =
    new Dictionary<County, Func<EFHomeownerQuote, decimal>>
    {
        [County.MA.Dukes] = q => ...,
    };
```

- An entry with a fixed result ignores its argument (`_ => true`). An entry that needs logic
  uses it.
- Declare it once, as a `static` get-only property.
- `IReadOnlyDictionary` over a `Dictionary` keeps hash lookups and the plain initializer. Use
  `ImmutableDictionary` only when the dictionary is handed to other code and has to be
  guaranteed unchangeable.
- The keys are the complete list of what behaves specially, and code can enumerate them. A test
  iterates the keys instead of keeping its own copy, so a new entry is covered the day it's added.
- Prefer it to an `if` or `switch` chain on the key, which buries the keys in control flow. When
  every member of a ClosedSet needs a result, use the generated `.Switch()`, which takes one
  branch per member.

Examples:
- `HomeownerQuoteFactory.ElementNeedsConfirmation`: element name to confirmation predicate
  (`Swyfft.Services/Quotes/Homeowner/HomeownerQuoteFactory.cs:440`, read at line 327)
- `HomeownerByPerilEngine.NamedStormMinimumByCounty`: county to named-storm deductible minimum
  (`Swyfft.Services/QuoteEngine/Homeowner/HomeownerByPerilEngine.cs:766`)
- `QuoteElementFactory.HomeownerElementFilters`, the element visibility filters: element name to
  visibility predicate (`Swyfft.Services/Helpers/QuoteElementFactory.cs:69`, read at line 46)
- `CountyDiscontinuedRule.Discontinued`: state and carrier to county predicate
  (`Swyfft.Services/RiskSelection/Homeowner/RiskRules/HardDecline/CountyDiscontinuedRule.cs:22`,
  read at line 189)
- `BuildingTypeExt.NonHabitationalDisallowed`: state to carrier predicate
  (`Swyfft.Common/SetDefinitions/CommonSets/BuildingTypeExt.cs:27`)

The first two already have this shape. `HomeownerElementFilters` and `Discontinued` are declared
`Dictionary`, and `NonHabitationalDisallowed` is declared `ImmutableDictionary`.

## Membership sets: named values that get special treatment

When some values of a type get special treatment, declare them as an `ImmutableHashSet`,
initialized with a collection expression and named for what membership means. Callers check
with `Contains`.

```csharp
public static ImmutableHashSet<RoofType> DurableRoofs { get; } =
[
    RoofType.ClayTile,
    RoofType.ConcreteTile,
    ...
];
```

- Use `{ get; } =`, not `=>`. An expression-bodied property builds a new set on every read.
  `QuoteConstants.cs:586-587` documents that cost on the `IsConfigSupported` path.
- A set computed from other data calls `.ToImmutableHashSet()` once, in the same `{ get; } =`
  form (`PreUpgradeConfirmationConfigs`, `QuoteConstants.cs:339-341`).
- When a base class needs each subclass to say where it applies, make the set a `virtual`
  property carrying the base's default, and let subclasses override it.
  `RiskRule.ApplicableWorkflows` works this way, and the base's `IsApplicable` reads it.
- A one-off check against two or three values can stay an inline `IsOneOf(...)`. Once the values
  mean something, or get checked in more than one place, they become a named set.
- The set can be enumerated, so a test iterates it instead of keeping its own copy.

Examples:
- `QuoteConstants.DurableRoofs` (`Swyfft.Services/Common/QuoteConstants.cs:367`)
- `QuoteConstants.FloodZonesThatRequireFloodInsurance` (`QuoteConstants.cs:284-285`)
- `ByPerilTerritoryRepository.SinkholeProductLineStates`
  (`Swyfft.Services/Common/ByPerilTerritoryRepository.cs:7-12`, read at line 23)
- `HomeownerEAndSByPerilPremiumGeneratorQbeTX.HasWindstormMitigationData`
  (`Swyfft.Services/Premium/Homeowner/TX/EAndS/HomeownerEAndSByPerilPremiumGeneratorQbeTX.cs:172`,
  read at line 165)
- `RiskRule.ApplicableWorkflows` and `LoggableWorkflows`, virtual sets that rules override
  (`Swyfft.Services/RiskSelection/RiskRule.cs:83-92`)
