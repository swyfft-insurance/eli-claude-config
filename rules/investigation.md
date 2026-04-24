# Investigation

> Gate 3 applies here — see `core-behavior.md`.

- **Never suspect established infrastructure.** Treat core Swyfft components (ClosedSets, SwyfftVersion, GetTableVersion, equality operators, DI, EF) the same as Microsoft framework code — assume they work unless there's a ticket explicitly changing them. If `==` or `GetTableVersion` were broken, hundreds of tests would fail, not 4. When something "seems wrong" with infrastructure, the bug is in YOUR code or YOUR understanding.
- **Check the full inheritance chain.** When investigating what a class does, read the ENTIRE chain from base to leaf — not just the leaf class. Claiming "this class doesn't override X" after only reading one file is wrong if you didn't read its parents.
