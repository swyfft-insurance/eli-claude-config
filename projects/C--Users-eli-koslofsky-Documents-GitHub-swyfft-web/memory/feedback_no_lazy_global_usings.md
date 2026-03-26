---
name: No lazy global usings
description: Never add global usings as a shortcut when only a few files need them — add usings to each file individually
type: feedback
---

Never add global usings as a shortcut for a few files. If 5 files need a using, add it to those 5 files. Adding to global usings is lazy and pollutes the entire project's namespace for no reason.

**Why:** Claude knew the correct fix but chose the shortcut — this is not acceptable. Shortcuts that affect the entire project to solve a local problem are code smells.

**How to apply:** When a build error says "type not found" in a few files, add the `using` to each file individually. Never touch `!_GlobalUsings.cs` unless the type is genuinely needed project-wide.
