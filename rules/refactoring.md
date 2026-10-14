# Refactoring Strategy

## Let the compiler find call sites, not grep

When changing a C# type, signature, member name or access modifier, make the change and build. The compiler lists every broken reference; don't grep to predict them.

## Don't cite a pattern you introduced earlier in the same branch as precedent

Justify an approach against the codebase's pre-existing convention, not against something new from the same PR.

## Contain a shared-base change by construction

A base-class change reaches every subclass. Make it provably inert for the subclasses you aren't targeting (identical behavior, unchanged inheritance, or reads and writes guarded by presence checks), or scope it to the targets. If proving that needs a run of every subclass, it isn't contained.

## A default element generator that stops changing constraint codes is a deletion candidate

When a refactor removes the last constraint code a generator added or removed, the generator produces exactly what its base does. If nothing inherits from it, delete it, then point its factory line at the base generator. Delete the factory line instead only when the next mapping below already points at the base (`DefaultElementGeneratorFactoryBase` resolves an unmapped version to the highest mapping below it). Ask before deleting an intermediary: that means repointing every generator that inherits from it and collapsing a version step.
