---
name: Fix access modifiers instead of changing functionality
description: When a method is inaccessible (private/internal), change the access modifier — don't rewrite the logic to avoid calling it
type: feedback
---

When a method is inaccessible due to its protection level, the fix is to change the access modifier (e.g., `private` → `protected`), NOT to rewrite the calling code to avoid the method entirely.

**Why:** Claude has repeatedly worked around access issues by completely changing functionality — removing code paths, simplifying logic, or skipping features — rather than making the trivial fix of changing `private` to `protected`. This produces worse code that silently drops planned behavior, and wastes time.

**How to apply:** When you hit a "inaccessible due to its protection level" error:
1. Change the access modifier. That's it.
2. If you're unsure whether changing the modifier is safe (e.g., it might break encapsulation), ASK the user — don't silently rewrite the logic instead.
3. Never treat an access modifier as immutable. They exist to be adjusted when inheritance hierarchies evolve.
