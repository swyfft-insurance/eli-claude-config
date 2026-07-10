# Refactoring Strategy

- **Let the compiler find call sites, not grep.** When refactoring a type, signature, member name, or access modifier in C# (a compiled language), make the change and build — the compiler flags every broken reference exactly. Don't grep to predict the breakage first; change it and let the build enumerate the work.
- **Don't cite a pattern you introduced earlier in the same branch as precedent.** Justify an approach against the pre-existing codebase convention, not against another new thing from the same PR.
- **Contain a shared-base change by construction.** A change to a base class reaches every subclass that inherits it. Make it provably inert for the subclasses you aren't targeting — identical behavior, unchanged inheritance, or reads/writes guarded by presence checks — or scope it to the targets. If you'd need to run every subclass to prove you didn't move one, the change isn't contained.
