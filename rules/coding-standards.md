---
audited-by: [code-complete]
---

# Coding Standards

## SOLID and DRY govern the design

New code conforms to SOLID and never repeats logic that already exists. A class the change already touches gets refactored to SOLID as part of the change: make a member `virtual` and override it, widen an access modifier, change a signature, extract a method or an interface, move logic to where it belongs. Never add a SOLID or DRY violation to avoid that refactor, such as a parallel member, a wrapper or a copy built around code that should change.

Once the change works, take a separate pass over every class it touched, ask what refactor would make that code cleaner, and make it.

- **Never be afraid to change our own code.** Our most valuable resources as C# engineers are that we code in an object-oriented language and that we control our own code. Use both: when existing code doesn't fit the change, change it, instead of coding around it.

## A static helper class only bridges unrelated class hierarchies

A static helper class is only for logic whose callers share no base class. Logic whose callers share one goes on that base.

## Put code in the class that already holds that kind of code

Before creating a class, search the codebase for the class that already holds that kind of code, and put the code there. Create a new class only when no existing one fits, and the plan says why.

## Identifier names must be self-documenting

- **Reveal intent to a reader who has never seen the code.** A name says what the thing is, what it holds or returns, and what it is for, read where it is used rather than where it is declared. Favor clarity over brevity.
- **Never mislead.** A name that suggests the wrong kind of thing fails even with every word in place: a value named like a condition, a yes/no named like a value, a single item named like a collection.
- **Grammar matches the kind of thing.** A method is a verb phrase. A variable, field, property, constant or type is a noun phrase or adjective. A yes/no is an affirmative phrase (`CanSeek`, never `CantSeek`), with `Is`, `Has` or `Can` only where it adds meaning. A collection is a plural phrase naming its items, never a singular word plus `List` or `Collection`.
- **Make every distinction meaningful.** Names that sit side by side differ in a word that says how the things differ. A number series (`premium1`, `premium2`), a noise word (`PolicyInfo` beside `PolicyData`) or an age word (`New`, `Old`, `Legacy`) distinguishes nothing.
- **One word per concept.** A concept keeps one word in every name and comment, and a word never stands for two concepts. `Fetch`, `Retrieve` and `Get` for the same operation fail.
- **Carry the context the reader lacks, not the context already present.** A name stays clear far from its declaration: a value says which form of a concept it holds when the concept exists in several forms. A name doesn't repeat what its type or enclosing member already says. Descriptiveness grows with scope: `i` is fine as a loop counter, `Num` is not as a class constant.
- **Use the domain's words.** A business concept takes its Swyfft term (`swyfft-domain.md` § "Swyfft/Insurance Terminology"). A technical one takes the programmer's term.
- **Abbreviate every word a reader still recognizes abbreviated.** Verbose means every part of the meaning is in the name, not that every word is spelled out.
- **A whole-word name past 40 characters is a violation.** A member, parameter, local or constant name that runs past 40 characters in whole words has skipped the abbreviation rule above. Class names are exempt: a class that shares a naming pattern with its sibling classes keeps it, however long.

**A name that scopes a thing to one carrier, state or product line stops fitting once another one uses it.** Move the thing to a home named for its shared meaning, and point every reader at the new name, the original owner's included. One carrier's code never reads another carrier's member (a QBE constant read by a Hadron rule). An existing read like that is a defect to fix, never a precedent for another.

## General

- Never add global usings. Add `using` to each file.
- Prefer collection expressions (`[a, b, c]`, `[.. source]`) over `new()`, `new T[] {}`, `new List<T> {}`, `.ToList()` and `.ToArray()` wherever the target type supports them, including `TheoryData<T>`.
- Build `TheoryData<T>` from an existing sequence with `.ToTheoryData()`, not `new TheoryData<T>()` plus `.Add(...)` in a loop. A hand-written literal set of rows can be a collection expression.
- An `if` condition carries as few negations as possible. Inverting the `if` and swapping its branches negates every term (`!a || !b || c` becomes `a && b && !c`), so an `if` whose terms are mostly negated is inverted. `if (!a || !b || c)` flips to `if (a && b && !c)`; `if (a || !b || c)` stays, since flipping it gives `!a && b && !c`.
- A tuple of more than two values is a `record` with named properties, wherever it appears: a theory row, a return type, a local, a collection element. `(HomeownerStateConfig Source, HomeownerStateConfig Target, MigrationFlow Flow)` becomes `record MigrationCase(HomeownerStateConfig Source, HomeownerStateConfig Target, MigrationFlow Flow)`.
- Use C#'s syntactic sugar wherever the repo's C# version supports it: target-typed `new(...)`, collection expressions, primary constructors, pattern matching, the `field` keyword. Root `AGENTS.md` names the version ("We use C# 14"), so the rule follows it as it changes.
- An argument gets its parameter name when the line doesn't show what it is: a bare `null`, `true`, `false` or number, or one of several arguments of the same type. `new BucketOverrideMigrationCase(InsuranceScore.NoResponse, InsuranceScore.From726To750, null, null, 738)` becomes `new BucketOverrideMigrationCase(ExpiringInsuranceScore: InsuranceScore.NoResponse, BucketOverride: InsuranceScore.From726To750, RenewalWholeNumberScore: null, RenewalScoreStatus: null, ExpectedWholeNumberOverride: 738)`.

## Never reinvent a Swyfft extension method

When a Swyfft extension method already does what new code needs, the code calls it instead of writing the logic out by hand. At code-complete, check every method and expression the diff adds against the extension methods on its receiver's type and on every interface that type implements, and replace each hand-written equivalent with the call. Find them by searching the solution for `this <TypeName>` for each of those types.

## Line Length

`.cs` lines, production and tests, stay at or below 120 characters including indent. Other file types are exempt. Wrap at natural punctuation: after commas, before operators, between chain links, after an opening paren. Peer items (theory rows, parameter lists, initializers) all use one wrapping pattern. The limit applies only to lines the change writes or modifies, including a line it re-indents; untouched long lines stay.

`~/.claude/scripts/Build-Solution.ps1` runs `~/.claude/scripts/Test-LineLength.ps1` as a pre-build gate, so a plan that builds needs no separate line-length step. Run `Test-LineLength.ps1 -Mode local` (or `-Mode branch`) on its own only when nothing builds. Self-check while editing; the script is a backstop.

**Line length never dictates code shape.** Wrap the line. Never restructure working code, split or merge a method, alter an approved design, or reopen a settled decision to make lines fit. A line-length violation is never a blocker, a HARD STOP, or an option put to Eli.

## Magic Numbers / Strings

Extract literals to named constants, including sentinels like `int.MaxValue` for "no limit". This applies to plan code excerpts too.

**Scope a constant to its only user.** A constant one method reads is a camelCase `const` at the start of that method (`const double metersPerKilometer = 1_000D;`). It moves to the class only when a second member needs it. A value that can't be `const`, such as an array, is a local in the same place.

## ClosedSets

ClosedSet usage rules live in `Swyfft.Common/SetDefinitions/CLAUDE.md`. Read it in full before writing or modifying any C# that touches a ClosedSet, even if you read it earlier in the session.

Before the code-complete HARD STOP, re-read it and audit every ClosedSet usage the diff adds or changes against every section of it. Fix every violation before announcing code-complete.

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

Example: `HomeownerByPerilEngine.NamedStormMinimumByCounty` (`Swyfft.Services/QuoteEngine/Homeowner/HomeownerByPerilEngine.cs`).

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
- When each subclass says where a base applies, make the set a `virtual` property carrying the base's default (`RiskRule.ApplicableWorkflows`, `Swyfft.Services/RiskSelection/RiskRule.cs`).
- Two or three values checked once can stay an inline `IsOneOf(...)`. Once they mean something or are checked in more than one place, name the set.
- Tests iterate the set rather than keeping their own copy.

Example: `QuoteConstants.DurableRoofs` (`Swyfft.Services/Common/QuoteConstants.cs`).
