# Coding Standards

## SOLID governs the design

New code conforms to SOLID. Existing code in scope gets refactored toward it when the refactor stays small: a rename, an extracted method, a narrowed interface. When the fix would go well past what the ticket asked, stop, name the violation, say what fixing it involves, and ask Eli how much of it belongs in this work.

## Identifier names must be self-documenting

An identifier (variable, property, method, parameter, field, constant, type) says what the thing holds or returns and what it is for. Prefer verbosity: `GetGroupRadix` fails, `GetElementCombinationPermutationCount` passes. Abbreviation is fine while the meaning survives (`CalcEachElementOptIterCount`). The test: read it at a use site with nothing else on screen. If it doesn't say what the thing is and what it's for, it is too short.

## General

- **We own this code. Its current shape is not a constraint on the solution.** Access modifiers, signatures, where a value is computed and how a class is split are all ours to change. Make the `private` member `protected`, widen the signature, or move the logic; never contort the approach to avoid touching existing code. Only external contracts (public APIs, on-disk and DB formats, regulatory rules) constrain, and those change with the right migration.
- Never add global usings. Add `using` to each file.
- Prefer collection expressions (`[a, b, c]`, `[.. source]`) over `new()`, `new T[] {}`, `new List<T> {}`, `.ToList()` and `.ToArray()` wherever the target type supports them, including `TheoryData<T>`.
- Build `TheoryData<T>` from an existing sequence with `.ToTheoryData()`, not `new TheoryData<T>()` plus `.Add(...)` in a loop. A hand-written literal set of rows can be a collection expression.

## Line Length

`.cs` lines, production and tests, stay at or below 120 characters including indent. Other file types are exempt. Wrap at natural punctuation: after commas, before operators, between chain links, after an opening paren. Peer items (theory rows, parameter lists, initializers) all use one wrapping pattern. The limit applies only to lines the change writes or modifies, including a line it re-indents; untouched long lines stay.

`~/.claude/scripts/Build-Solution.ps1` runs `~/.claude/scripts/Test-LineLength.ps1` as a pre-build gate, so a plan that builds needs no separate line-length step. Run `Test-LineLength.ps1 -Mode local` (or `-Mode branch`) on its own only when nothing builds. Self-check while editing; the script is a backstop.

**Line length never dictates code shape.** Wrap the line. Never restructure working code, split or merge a method, alter an approved design, or reopen a settled decision to make lines fit. A line-length violation is never a blocker, a HARD STOP, or an option put to Eli.

## Magic Numbers / Strings

Extract literals to named constants, including sentinels like `int.MaxValue` for "no limit". This applies to plan code excerpts too.

**Scope a constant to its only user.** A constant one method reads is a camelCase `const` at the start of that method (`const double metersPerKilometer = 1_000D;`). It moves to the class only when a second member needs it. A value that can't be `const`, such as an array, is a local in the same place.

## ClosedSets

ClosedSet usage rules live in `Swyfft.Common/SetDefinitions/CLAUDE.md`. Read it in full before writing or modifying any C# that touches a ClosedSet, even if you read it earlier in the session.

Before the code-complete HARD STOP, re-read it and audit every ClosedSet usage the diff adds or changes: parameters typed as the ClosedSet, not `string`/`int`; `.Value` only at true system boundaries (external APIs, IMS, raw storage); comparisons and `.Switch()` in the documented forms. Fix every violation before announcing code-complete.

## Dispatch dictionaries: behavior keyed by a value

When only some keys behave specially, declare a `static` get-only `IReadOnlyDictionary` from key to function, backed by a plain `Dictionary`, with one entry per special key. Callers use `TryGetValue`; a missing key takes the default behavior.

```csharp
private static IReadOnlyDictionary<County, Func<EFHomeownerQuote, decimal>> NamedStormMinimumByCounty { get; } =
    new Dictionary<County, Func<EFHomeownerQuote, decimal>>
    {
        [County.MA.Dukes] = q => ...,
    };
```

- A fixed-result entry ignores its argument (`_ => true`).
- Use `ImmutableDictionary` only when the dictionary is handed to other code and must be guaranteed unchangeable.
- Tests iterate the keys rather than keeping their own copy.
- Prefer this to an `if` or `switch` chain on the key. When every member of a ClosedSet needs a result, use the generated `.Switch()`.

Example: `HomeownerByPerilEngine.NamedStormMinimumByCounty` (`Swyfft.Services/QuoteEngine/Homeowner/HomeownerByPerilEngine.cs:766`).

## Membership sets: named values that get special treatment

When some values of a type get special treatment, declare an `ImmutableHashSet` named for what membership means, initialized with a collection expression. Callers use `Contains`.

```csharp
public static ImmutableHashSet<RoofType> DurableRoofs { get; } =
[
    RoofType.ClayTile,
    RoofType.ConcreteTile,
    ...
];
```

- Use `{ get; } =`, never `=>`, which builds a new set on every read. A computed set calls `.ToImmutableHashSet()` once, in the same form.
- When each subclass says where a base applies, make the set a `virtual` property carrying the base's default (`RiskRule.ApplicableWorkflows`, `Swyfft.Services/RiskSelection/RiskRule.cs:83-92`).
- Two or three values checked once can stay an inline `IsOneOf(...)`. Once they mean something or are checked in more than one place, name the set.
- Tests iterate the set rather than keeping their own copy.

Example: `QuoteConstants.DurableRoofs` (`Swyfft.Services/Common/QuoteConstants.cs:367`).
