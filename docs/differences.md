Differences from USB Logo
=========================


While Lunar is definitely a Logo, it's not compatible with older dialects. Programmers used to, say, UCB Logo -- the *de facto* standard -- may be tripped by a number of differences:

- Literal lists can't span lines.
- You can't quote a word, only a list. But words can be taken literally.
- Lists are internally implemented as dynamic arrays.
- `setitem` operates on lists, not arrays (which aren't implemented).
- `array` emits a list, for the same reason.
- Arithmetic operators are `add`, `sub`, `mul`, `div`; there are no infix versions.
- Comparison operators are `lt`, `lte`, `eq`, `neq`, `gt`, `gte`; no infix versions here, either.
- predicate names are prefixed with "is-" instead of suffixed with "p".
- The programmer defines *functions*. The interpreter supplies *procedures*.
- Scoping is lexical; you can do dynamic scoping as well, but not with functions.
- Flow control is done with break/continue/return, like in modern languages; `continue` means something else than in UCB Logo.
- There's no template iteration; `foreach` uses an ordinary variable, while `apply`, `map` and `filter` take a function.
- First-class dictionaries replace property lists, with different accessors.
- `count` is extended to work on dictionaries.
- `catch` and `throw` work differently.

Blocks of code are, of course, new to Lunar Logo, and they are used instead of lists in several places.
