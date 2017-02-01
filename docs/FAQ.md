Frequently Asked Questions
==========================


**Q: What's the difference between a literal list and a block of code?**

A: A block of code has already been parsed, so it may contain items of any type, while a literal list contains only strings. A literal list is also expected as the condition to `while`, a function's argument list or the return values of `ifelse`. But internally they are both just lists.

**Q: What if I want to call a function for its side effects, ignoring the return value?**

A: Prefix the call to it with `ignore` -- it's a built-in procedure that does exactly what it says on the tin.

Absent features
---------------

**Q: Why are there no increment and decrement operators?**

A: I tried to add a couple, and it just didn't work out. They don't fit in with the rest of the language aesthetically, and encourage the wrong kind of coding style.

**Q: Why is there no `is-nil`?**

A: Because `nil` isn't a data type in Lunar Logo. On the contrary, it denotes the explicit absence of any value that could *have* a type. The right way to test for it is with `eq` or `neq` -- the only comparisons `nil` supports.

**Q: Why is there no `repeat` and `forever`?**

A: Two reasons: they're kind of redundant, and implementing them is an iffy proposition, as Lunar Logo doesn't support any form of template iteration.

Interpreter internals
---------------------

**Q: Is Lunar Logo embeddable?**

A: Definitely! The Python implementation will behave like an ordinary module when imported; for the Go edition, simply remove the supplied `main()` function and optionally rename the package.
