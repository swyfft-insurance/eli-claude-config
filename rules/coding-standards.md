# Coding Standards

## SOLID governs the design

New code conforms from the start.

Existing code gets refactored toward SOLID when it is already in scope and the refactor stays
small. A rename, an extracted method, a narrowed interface: do it as part of the change.

When the fix would push well past what the ticket asked for, stop. Name the violation, say what the
fix would involve, and ask how much of the fix belongs in the pull request, user story, or bug being
worked on, if any. That call is Eli's.

## General

- **We own this code. Its current shape is not a constraint on the solution.** Access modifiers, method signatures, where a value is computed, how a class is split: all of it is ours to change as part of the work. If the clean approach needs a `private` member made `protected`, a signature widened, or logic moved, change it; never contort the approach to avoid touching existing code. "It's written this way now" is not a reason. The only real constraints are external (public API contracts, on-disk/DB formats, regulatory rules), and even those change with the right migration. (Most common instance: fix `private` → `protected` instead of rewriting logic to dodge the call. Never treat access modifiers as immutable.)
- Never add global usings as a shortcut. Add `using` to each file individually.
- Prefer collection expressions (`[a, b, c]`, `[.. source]`) over `new()`, `new T[] {}`, `new List<T> {}`, and `.ToList()`/`.ToArray()` wherever the target type supports them, including `TheoryData<T>`. This is the default for collection initialization and construction.
- Prefer `.ToTheoryData()` to build `TheoryData<T>` from an existing sequence/query rather than hand-rolling `new TheoryData<T>()` + `.Add(...)` in a loop. (For a hand-written literal set of rows, a collection expression `[...]` is fine.)
