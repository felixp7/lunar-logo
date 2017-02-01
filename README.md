Lunar Logo
==========


Welcome to Lunar Logo, an experimental scripting language based on Logo and Lua, with a tiny core and clean, minimal syntax. Example usage:

	$ ./lunar.py sqrt add mul 3 3 mul 4 4
	5.0

That's right, you can type Lunar Logo code at a Bash prompt without escaping it (within reason). For a bigger sample, put this code in a file, say `repl.lulz`:

	print [Welcome to Lunar Logo. Enter your commands, or BYE to quit.]
	while [true] do
		type >
		type space
		make cmd readlist
		if eq 0 count :cmd do
			continue
		end
		if eq bye lowercase first :cmd do
			break
		end
		foreach i results parse :cmd do
			if neq :i nil do
				show :i
			end
		end
	end

Now you can load it as follows:

	$ ./lunar.py load repl.lulz

Indeed, Lunar Logo doesn't need a built-in interactive mode because you can code one yourself in just a few lines!

Features
--------

- A blend of two programming languages famous for friendliness.
- First-class functions with lexical scoping (and blocks with dynamic scoping).
- Metaprogramming: code is data; the parser and evaluator are procedures in the language.
- Tiny core: under 200 lines of code in the prototype -- squeaky-clean code, too!
- Easily extensible and embeddable: many built-in procedures are literal one-liners.

Project goals
-------------

- A language that needs little or no escaping when embedded into string literals, command lines and such.
- A language that doesn't run *too* slowly when implemented in another interpreted language.
- A language that throws few exceptions. A surprising amount of modern languages in widespread use have other error handling mechanisms.

Uses
----

Lunar Logo is designed to be used as a command language for driving larger applications. Imagine a command-line parser that can understand any instructions rather than just flags and options!

History
-------

This is the second time I do a Logo dialect. [The first time around][ll] I kept much closer to the original language, but the result was a messy implementation that left much of the heavy lifting to individual procedures, and still didn't have much in the way of speed or capabilities.

[ll]: http://felixplesoianu.github.io/little-logo/

Status
------

As of 31 January 2017, Lunar Logo has two implementations that can run all the examples correctly. The language supports over 100 procedures (you can find a concise list at the end of `lunar.py`). See the tutorial for an overview.

The software is considered alpha quality. Testing has been limited so far, and the feature set is still in flux. Anything mentioned in the tutorial and examples should stay put from now on, though.

To Do
-----

Error reporting needs some way to provide better context.
