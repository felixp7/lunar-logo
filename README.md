Lunar Logo
==========


Welcome to Lunar Logo, a toy scripting language based on Logo and Lua, with a tiny core and very clean syntax, currently implemented as a stand-alone Python module. Example usage:

	$ ./lunar.py sqrt add mul 3 3 mul 4 4
	5.0

That's right, you can type Lunar Logo code at a Bash prompt without escaping it (within reason). For a bigger sample, put this code in a file, say `benchmark1.lulz`:

	-- Loop-and-math benchmark
	make start timer
	make a 1
	for i 1 1000 1 do
		make a add div :a 2 div :a 3
	end
	print :a
	make finish timer
	print sub :finish :start

Now you can load it as follows:

	$ ./lunar.py load benchmark1.lulz
	6.588005489477243e-80
	0.21355808000000004

Yes, it's slow. You're not going to write real time games in Lunar Logo. Still reasonably fast for something implemented in under 300 lines of Python. Speaking of which.

Project goals
-------------

- A language that needs little or no escaping when embedded into string literals, command lines and such.
- A language that doesn't run *too* slowly when implemented in another interpreted language.
- A language that throws few exceptions. A surprising amount of modern languages in widespread use have other error handling mechanisms.

History
-------

This is the second time I do a Logo dialect. [The first time around][ll] I kept much closer to the original language, but the result was a messy implementation that left much of the heavy lifting to individual procedures, and still didn't have much in the way of speed or capabilities.

[ll]: http://felixplesoianu.github.io/little-logo/

Status
------

As of 21 January 2017, Lunar Logo supports 55 procedures (you can find the list at the end of `lunar.py`), including flow control. There are no functions yet; calling `return` will just end the program. For now, you can store a block of code in a variable (code is data in Logo!) and run it repeatedly:

	make greeting do
		print results parse [Hello, :you !]
	end

	make you stranger
	run :greeting
	type [What's your name?]
	make you readword
	run :greeting

For that matter, calling `break` outside of a loop will also end the program, since there will be nothing to stop the condition from propagating; only `continue` will work correctly anywhere.

Thanks for reading. More to come.
