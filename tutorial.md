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
- A word starting with "[" (open square bracket) introduces a *literal list*, that continues until the first word ending in "]" (closed square bracket). A literal list must end on the same line, otherwise you'll get an error. Literal lists can't be nested, either.
- A word starting with ":" (a colon) denotes variable lookup. You only use a colon prefix when taking the value of a variable, not when creating it.
- `make` and `print` are *procedures* built into the language. You can't use those words for any other purpose, except with special escaping.
- For that matter, `load` is also an ordinary procedure. You can give any Logo code as command-line arguments to `lunar.py`, like this:

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

The keyword `do` introduces a block of code, that goes on until the matching `end`. Blocks can be nested, and/or span multiple lines, but otherwise are ordinary lists you can store in a variable, as above. The `run` procedure will evaluate the code inside on demand. A couple more notes:

- `type` is like `print`, except it doesn't emit a newline at the end.
- Because literal whitespace separates words, you have to be explicit about emitting it.
- The language is case-insensitive: `print`, `Print` and `PRINT` all mean the same thing. Case is preserved, however, inside literal lists, and in words that mean nothing to the interpreter.

But that's a primitive way to reuse code. To get serious, you'll want *functions*:

	-- A named function...
	function avg [a b] do
		return div add :a :b 2
	end

	-- ...can be called like this...
	print avg 5 10

	-- ...or indirectly like this...
	print apply :avg list 5 10

	-- ...and is completely equivalent to:
	make avg2 fn [a b] do
		return div add :a :b 2
	end
	-- (Can't reuse the same name.)

	-- Just to make sure now.
	print avg2 5 10

Once defined, functions can be called just like procedures, but in reality they live in variables, and can be passed around like any other value. You just can't easily store something else in the same variable after defining it to be a function.

A function (or procedure) doesn't have to return a value, but if it does, you have to use it. Try removing the word "print" on the last line, and see what happens. This is to prevent simple spelling mistakes from causing hard-to-track errors. To rehash an earlier example, can you spot the typo on the next line?

	sqr add mul 3 3 mul 4 4

Anyway, there is more that Lunar Logo can do for you: logic, trigonometry, list and string processing, even random number generation for simple games. But for now, let's start with the basics.

Data types
----------

You've already met literal lists. Let's see how `lunar.py` parses other kinds of words:

- `true` and `false` are read as the corresponding boolean value.
- `nil` is read as, well, the nil value (a.k.a. "null" or "None" in other languages).
- The name of a built-in procedure is parsed accordingly. (Procedures are values too.)
- A word consisting of only digits, with an optional minus sign in front, is read as an integer.
- Last, the parser tries converting the word to a floating point number.
- If all else fails, the word is kept as-is, becoming a character string.

Speaking of lists, there are some tricks I haven't mentioned:

- An empty pair of square brackets, with or without spaces in-between, is read as a list with no elements.
- The closing square bracket only counts if it ends a word. The characters "[[]]" parse as a list with one element, the word "[]".
- You can use `parse` to re-process literals. `parse [[]]` yields a list with one element, the empty list.

Last but not least, there are two other data types, dictionaries and functions, that can't be parsed directly but can be created with the procedures `dict` and `function`/`fn`, respectively. Blocks of code, too, are evaluated at runtime, after the parsing stage.

Conditionals
------------

You've already seen how to store a sequence of operations in a block of code. Now let's look at how to express when it's OK to run them.

	type [Enter a number:]
	type space
	make num parse-int readword

	if lt :num 0 do
		print [Don't be so negative!]
	end

`if` takes a condition and a block of code and runs the block only if the condition holds true. But what if you want to (also) do something otherwise? Append this to the previous example:

	test eq mod :num 2 0
	iftrue do
		print [I don't even.]
	end
	iffalse do
		print [That's odd...]
	end

You can use `iffalse test ...` to chain conditionals, similar to "else if" clauses in other languages. That, however, can be unwieldy if you just want to set a value based on a condition. Let's expand the example some more:

	function odd-or-even [n] do
		return ifelse eq mod :n 2 0 [even] [odd]
	end

	print odd-or-even :num

Unlike its brethren, `ifelse` takes a condition and two *literal lists*. It parses and evaluates only one of them, depending on the condition, and returns the first resulting value. It's an error to pass `ifelse` an empty list.

As an aside, note how procedure and function names can contain "strange" characters like a dash. That's thanks to the split-at-whitespace rule.

Loops
-----

Now let's see how to run some code repeatedly, either a fixed number of times or while a condition is met. To wit:

	for i 1 10 1 do
		type :i
		type tab
		type mul :i 2
		type tab
		print pow :i 2
	end

`for` takes a variable name followed by three numbers: the initial value, limit and step size (the step size is required), and runs the given block of code with the variable stepping through the interval thus defined.

To loop over more arbitrary data, use `foreach` instead:

	foreach i [1 2 3 5 8] do
		print sqrt :i
	end

Except the code above will give an error message. Why? Because the members of a literal list are character strings. You have to parse them explicitly first:

	foreach i parse [1 2 3 5 8] do
		print sqrt :i
	end

And no, `foreach` won't do that by itself because you might want to pass it a list that's already stored in a variable, read from the user or built at runtime. It's not the computer's business to try and guess what you want!

Sometimes, though, you just don't know how many times you need to loop around. `while` can help with that:

	make n 156
	while [gte :n 1] do
		make n div :n 2
	end
	print :n

The list passed to `while` follows the same rule as those passed to `ifelse`.

Flow control
------------

This is all good and well, but sometimes you want to leave a loop early, when some special condition is met.

	make i 1
	while [lte :i 5] do
		print results parse [:i times through the loop.]
		type [Quit (y/n)?]
		type space
		make answer lowercase first readword
		if eq :answer y do
			break
		end
		make i add :i 1
	end

Nothing special there, just that `break` ends the innermost loop right there. To end just the current iteration, use `continue` instead.

	foreach i parse [1 2 3 5 8] do
		if eq mod :i 2 0 do
			continue
		end
		print :i
	end

There's also `return`, that returns a value from a function (early or not), but that can wait until next section.

Variable scope
--------------

Until now you've only created variables in the main body of the program. That's all good and well. But when working with functions, often you don't want their own local variables to spill out and clog the rest of the code. That's why each new function creates its own *scope*:

	function index-of [needle haystack] do
		localmake idx 0
		foreach i :haystack do
			if eq :i :needle do
				return :idx
			end
			make idx add :idx 1
		end
		return -1
	end

	print index-of c [a b c d e]
	print index-of f [a b c d e]
	-- print :idx

If you uncomment the last line, you'll get an error, because `idx` is created local to the function, and ceases to exist after the function returns (another thing this example illustrates). You can change that by replacing the `localmake` in line 2 with vanilla `make`. The latter, you see, creates a global variable if it can't find a local one to update. Function arguments, however, are always local, and so is the variable in a `foreach` or `for` loop. That increases both performance and safety.

(For advanced programmers, Lunar Logo has lexical scope, with all that implies.)

Error handling
--------------

An error can happen at any time while running a Logo program. By default, that ends the run right there. But that makes programs rather frail, so Lunar gives you a way to catch errors when they happen and do something sensible about them.

	catch error do
		sqrt 2
	end

	if neq :error nil do
		type [Caught error:]
		type space
		print :error
	end

	catch error do
		print [Before throwing.]
		throw Aborted.
		print [After throwing.]
	end

	if neq :error nil do
		type [Caught error:]
		type space
		print :error
	end

`catch` simply runs the given block of code; if there was an error along the way, the error data will be placed in the given variable ("error" is just another name). Otherwise, the variable will be nil. Either way, the program will continue normally instead of being interrupted.

You can throw your own errors with `throw`. `catch` makes no difference between yours and those thrown by the language itself. If you need to tell them apart, inspect the error data in your code.

Restrictions
------------

By design, vanilla Lunar Logo can't connect to the Internet, access the file system or run other programs. That's to keep scripts obtained from untrusted sources from messing up your computer. Specialized applications may extend the language with their own procedures.
