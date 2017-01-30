Frequently Asked Questions
==========================


**Q: What's the difference between a literal list and a block of code?**

A: A block of code can contain items of any type, but a literal list contains only strings, so it can be safely passed to `parse`. A literal list is also expected as the condition to `while`, a function's argument list or the return values of `ifelse`.

**Q: What if I want to call a function for its side effects, ignoring the return value?**

A: Prefix the call to it with `ignore` -- it's a built-in procedure that does exactly what it says on the tin.

