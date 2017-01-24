Lunar Logo Tutorial
===================


Welcome to Lunar Logo, a modern scripting language with retro sensibilities. Lunar Logo isn't really meant to be used on its own; you're more likely to find it as part of another application. But you can try it out by itself, if only as a fancy calculator with some extra tricks.

I'll assume you know how to download and run the prototype interpreter `lunar.py`. If not, please refer to the user manual for your Python 3 runtime (you'll need one installed to run Lunar Logo). `lunar.py` is a command-line program, so you'll need to run it from Terminal, Command Prompt, or what have you.

To begin with, type the code below into a file, say `hello.lulz` (the file extension doesn't matter):

	-- The traditional programmer's greeting.

	make greeting [Hello, world!]
	print :greeting

You can run this first script with the following command:

	./lunar.py load hello.lulz

Did it work? Good! Now let's take a closer look at the code.

- A Lunar Logo program is made of *words* separated by whitespace.
- A word starting with "--" (two dashes) introduces a comment, that continues to the end of the line.
- A word starting with "[" (open square bracket) introduces a *literal list*, that continue until the first word ending in "]" (closed square bracket). A literal list must end on the same line, otherwise you'll get an error.
- A word starting with ":" (a colon) denotes variable lookup. You only use a colon prefix when taking the value of a variable, not when creating it.
- `make` and `print` are *procedures* built into the language. You can't use those words for any other purpose, except with special escaping.
- For that matter, `load` is also an ordinary procedure. You can give arbitrary Logo code as command-line arguments to `lunar.py`, like this:

	./lunar.py sqrt add mul 3 3 mul 4 4

Notice how arithmetic operators come before the operands; it's called [Polish Notation][wiki], and it's part of what makes Lunar so simple and clean. But stringing too much code on the command line makes it hard to read. Besides, what if you want to run the same bit of code in several places? Let's look at another example:

[wiki]: https://en.wikipedia.org/wiki/Polish_notation

	make greeting do
		print list Hello, :you
	end

	make you stranger
	run :greeting
	type [What's your name?]
	type space
	make you readword
	run :greeting

The keyword `do` introduces a block of code, that continues until the matching `end`. Blocks can be nested, and/or span multiple lines, but otherwise are ordinary lists you can store in a variable, as above. The `run` procedure will evaluate the code inside on demand. A couple more notes:

- `type` is like `print`, except it doesn't emit a newline at the end.
- Because literal whitespace separates words, we have to be explicit about emitting it.

But that's a primitive way to reuse code. To get serious, you'll want *functions*:

	-- A named function...
	function avg [a b] do
		return div add :a :b 2
	end

	-- ...can be called like this...
	print avg 5 10

	-- ...or indirectly like this...
	print apply :avg [5 10]

	-- ...and is completely equivalent to:
	make avg2 fn [a b] do
		return div add :a :b 2
	end
	-- (Can't reuse the same name.)

	-- Just to make sure now.
	print avg2 5 10

Once defined, functions can be called just like procedures, but in reality they live in variables, and can be passed around like any other value. You just can't easily store something else in the same variable after defining a function.

A function doesn't have to return a value, but if it does, you have to use it. Try removing the word "print" on the last line, and see what happens. This is to prevent simple spelling mistakes from causing hard-to-track errors. To rehash an earlier example, can you spot the typo on the next line?

	sqr add mul 3 3 mul 4 4

Anyway, there is more that Lunar Logo can do for you: logic, trigonometry, list and string processing, even random number generation for simple games. You can get a full list of procedures with `print sorted keys procedures`. Don't panic!

(To be continued.)
