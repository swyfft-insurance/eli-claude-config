# Coding Standards

- Fix access modifiers (`private` → `protected`) instead of rewriting logic to avoid the call. Never treat access modifiers as immutable.
- Never add global usings as a shortcut. Add `using` to each file individually.
- Prefer collection expressions (`[a, b, c]`, `[.. source]`) over `new()`, `new T[] {}`, `new List<T> {}`, and `.ToList()`/`.ToArray()` wherever the target type supports them — including `TheoryData<T>`. This is the default for collection initialization and construction.
- Prefer `.ToTheoryData()` to build `TheoryData<T>` from an existing sequence/query rather than hand-rolling `new TheoryData<T>()` + `.Add(...)` in a loop. (For a hand-written literal set of rows, a collection expression `[...]` is fine.)
