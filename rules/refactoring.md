# Refactoring Strategy

- **Let the compiler find call sites, not grep.** When refactoring a type, signature, member name, or access modifier in C# (a compiled language), make the change and build — the compiler flags every broken reference exactly. Don't grep to predict the breakage first; change it and let the build enumerate the work.
