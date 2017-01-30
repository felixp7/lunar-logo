#!/usr/bin/env python3

"""Clean, minimal scripting language based on Logo and Lua."""

from __future__ import division
from __future__ import print_function

import math
import random
import time

class Scope:
	def __init__(self, parent = None):
		self.names = {}
		self.parent = parent
		
		self.test = False
		
		self.continuing = False
		self.breaking = False
		self.returning = False
	
	def get(self, key, default=None):
		if key in self.names:
			return self.names[key]
		elif self.parent != None:
			return self.parent.get(key, default)
		else:
			return default
	
	def __getitem__(self, key):
		if key in self.names:
			return self.names[key]
		elif self.parent != None:
			return self.parent[key]
		else:
			raise KeyError("Undefined variable: " + str(key))
	
	def __setitem__(self, key, value):
		if key in self.names:
			self.names[key] = value
		elif self.parent != None:
			self.parent[key] = value
		else:
			#raise KeyError("Undefined variable: " + str(key))
			self.names[key] = value

class Closure:
	def __init__(self, arglist, code, scope):
		self.arglist = arglist
		self.code = code
		self.scope = scope

	def __call__(self, args):
		local = Scope(self.scope)
		for name, val in zip(self.arglist, args):
			local.names[name] = val
		return run(self.code, local)
		
	def __str__(self):
		return ("fn [" + " ".join(self.arglist) + "] do "
			+ " ".join([str(i) for i in self.code]) + " end")

def eval_next(code, cursor, scope):
	value = code[cursor]
	if type(value) == tuple:
		cursor += 1
		args = []
		for i in range(value[0]):
			if cursor >= len(code):
				raise SyntaxError(
					"Not enough arguments.")
			tmp, cursor = eval_next(code, cursor, scope)
			args.append(tmp)
		return value[1](scope, *args), cursor
	elif type(value) != str:
		return value, cursor + 1
	elif value[0] == ":":
		name = value[1:]
		# Expect name to be already lowercased.
		return scope[name], cursor + 1
	elif value == "do":
		return scan_block(code, cursor + 1)
	else:
		closure = scope.get(value.lower(), value)
		if isinstance(closure, Closure):
			cursor += 1
			args = []
			for i in range(len(closure.arglist)):
				if cursor >= len(code):
					raise SyntaxError(
						"Not enough arguments to "
						+ value.lower())
				tmp, cursor = eval_next(code, cursor, scope)
				args.append(tmp)
			return closure(args), cursor
		else:
			return value, cursor + 1

def scan_block(code, cursor):
	block = []
	while code[cursor] != "end":
		if code[cursor] == "do":
			tmp, cursor = scan_block(code, cursor + 1)
			block.append(tmp)
		else:
			block.append(code[cursor])
			cursor += 1
		if cursor >= len(code):
			raise SyntaxError(
				"Unexpected end of input in block.")
	return block, cursor + 1

# Essential procedures.
def parse(words):
	code = []
	buf = None
	in_list = False
	for i in words:
		if in_list:
			if i.endswith("]"):
				if len(i) > 1:
					buf.append(i[:-1])
				code.append(buf)
				in_list = False
			else:
				buf.append(i)
		elif i == "[]":
			code.append([])
		elif i.startswith("["):
			if i.endswith("]"):
				code.append([i[1:-1]])
			else:
				buf = []
				if len(i) > 1:
					buf.append(i[1:])
				in_list = True
		elif i.startswith("--"):
			break
		elif i.startswith(":"):
			code.append(i.lower())
		elif i.lower() in ["do", "end"]:
			code.append(i.lower())
		elif i.lower() == "true":
			code.append(True)
		elif i.lower() == "false":
			code.append(False)
		elif i.lower() == "nil":
			code.append(None)
		elif i.lower() in procedures:
			code.append(procedures[i.lower()])
		elif i.isdigit() or i[0] == "-" and i[1:].isdigit():
			code.append(int(i))
		else:
			try:
				code.append(float(i))
			except ValueError:
				code.append(i)
	if in_list:
		raise SyntaxError("Unclosed list at end of line.")
	else:
		return code

def run(code, scope):
	"""Underlies most other control structures."""
	cursor = 0
	while cursor < len(code):
		value, cursor = eval_next(code, cursor, scope)
		if scope.continuing or scope.breaking:
			return None
		elif scope.returning:
			return value
		elif value != None:
			raise ValueError(
				"You don't say what to do with: "
					+ str(value))

def results(code, scope):
	"""Underlies while, ifelse and the command line."""
	values = []
	cursor = 0
	while cursor < len(code):
		val, cursor = eval_next(code, cursor, scope)
		if scope.returning:
			return [val]
		elif scope.breaking or scope.continuing:
			break
		values.append(val)
	return values

def load(filename, scope):
	code = []
	with open(filename, "r") as f:
		for i in f:
			code.extend(parse(i.split()))
	return run(code, scope)

# Flow control
def do_continue(scope):
	scope.continuing = True

def do_break(scope):
	scope.breaking = True

def do_return(value, scope):
	scope.returning = True
	return value

# Error handling
def throw(message):
	raise RuntimeError(message)

def catch(varname, code, scope):
	varname = varname.lower()
	scope.names[varname] = None
	try:
		return run(code, scope)
	except Exception as e:
		scope.names[varname] = str(e)

# Printing out.
def do_print(value):
	"""Emit given value to standard output, followed by a newline."""
	if type(value) == list:
		# Turns out .join() wants all list elements to be strings.
		return print(" ".join([str(i) for i in value]))
	else:
		return print(value)

def do_type(value):
	"""Emit given value to standard output, without a newline."""
	if type(value) == list:
		# Turns out .join() wants all list elements to be strings.
		return print(" ".join([str(i) for i in value]), end='')
	else:
		return print(value, end='')

# Creating variables.
def make(varname, value, scope):
	"""If varname exists, change its value, else define it globally."""
	scope[varname.lower()] = value

def localmake(varname, value, scope):
	"""Define a local variable."""
	scope.names[varname.lower()] = value

def local(varname, scope):
	"""Declare a local variable, or several in a list."""
	if type(varname) == list:
		for i in varname:
			scope.names[i.lower()] = None
	else:
		scope.names[varname.lower()] = None

# Conditionals.
def do_if(cond, code, scope):
	if cond: return run(code, scope)

def do_ifelse(cond, ift, iff, scope):
	"""Ternary operator -- returns a value, unlike if/iftrue/iffalse."""
	if cond:
		return results(parse(ift), scope)[0]
	else:
		return results(parse(iff), scope)[0]

def do_test(cond, scope):
	scope.test = cond

def do_iftrue(code, scope):
	if scope.test:
		return run(code, scope)

def do_iffalse(code, scope):
	if not scope.test:
		return run(code, scope)

# Loops.
def do_while(cond, code, scope):
	"""While loop."""
	while results(cond, scope)[0]:
		value = run(code, scope)
		if scope.returning:
			return value
		elif scope.continuing:
			scope.continuing = False
		elif scope.breaking:
			scope.breaking = False
			break

def do_for(varname, init, limit, step, code, scope):
	"""For loop; the variable is always treated as local."""
	varname = varname.lower()
	scope.names[varname] = init
	if limit >= init:
		while scope.names[varname] <= limit:
			value = run(code, scope)
			if scope.returning:
				return value
			elif scope.continuing:
				scope.continuing = False
			elif scope.breaking:
				scope.breaking = False
				break
			scope.names[varname] += step
	else:
		while scope.names[varname] >= limit:
			value = run(code, scope)
			if scope.returning:
				return value
			elif scope.continuing:
				scope.continuing = False
			elif scope.breaking:
				scope.breaking = False
				break
			scope.names[varname] += step

def do_foreach(varname, items, code, scope):
	"""Foreach loop; the variable is always treated as local."""
	varname = varname.lower()
	for i in items:
		scope.names[varname] = i
		value = run(code, scope)
		if scope.returning:
			return value
		elif scope.continuing:
			scope.continuing = False
		elif scope.breaking:
			scope.breaking = False
			break

# Functions.
def fn(arglist, code, scope):
	"""Create a closure over the current scope and return it."""
	return Closure([i.lower() for i in arglist], code, scope)

def function(name, arglist, code, scope):
	"""Define a named function in the current scope."""
	scope.names[name.lower()] = Closure(
		[i.lower() for i in arglist], code, scope)

def do_map(closure, args):
	"""Map a user-defined function to the given argument list."""
	return [closure([i]) for i in args]

def do_filter(closure, args):
	"""Filter the given argument list by a user-defined function."""
	return [i for i in args if closure([i])]

# Lists.
def iseq(init, limit):
	"""Return a sequential list of integers from init to limit."""
	if init <= limit:
		return list(range(init, limit + 1))
	else:
		return list(range(init, limit - 1, -1))

def setitem(idx, seq, value):
	seq[idx] = value

# Dictionaries.
def do_dict(init):
	"""Return new dictionary off a list of alternating keys and values."""
	dictionary = {}
	i = 0
	while i < len(init):
		key = init[i]
		i += 1
		value = i < len(init) and init[i] or None
		dictionary[key] = value
		i += 1
	return dictionary

def put(dictionary, key, value):
	dictionary[key] = value

def do_del(dictionary, key):
	del dictionary[key]

procedures = {
	"parse": (1, lambda scope, code: parse(code)),
	"run": (1, lambda scope, code: run(code, scope)),
	"results": (1, lambda scope, code: results(code, scope)),
	"load": (1, lambda scope, f: load(f, scope)),
	"ignore": (1, lambda scope, value: None),
	
	#"procedures": (0, lambda scope: procedures),
	#"locals": (0, lambda scope: scope.names),

	"throw": (1, lambda scope, msg: throw(msg)),
	"catch": (2, lambda scope, name, code: catch(name, code, scope)),
	
	"break": (0, lambda scope: do_break(scope)),
	"continue": (0, lambda scope: do_continue(scope)),
	"return": (1, lambda scope, value: do_return(value, scope)),

	"print": (1, lambda scope, item: do_print(item)),
	"type": (1, lambda scope, item: do_type(item)),
	"show": (1, lambda scope, item: print(item)),
	
	"readlist": (0, lambda scope: input().split()),
	"readword": (0, lambda scope: input()),

	"make": (2, lambda scope, a, b: make(a, b, scope)),
	#"name": (2, lambda scope, a, b: make(b, a, scope)),
	"local": (1, lambda scope, n: local(n, scope)),
	"localmake": (2, lambda scope, a, b: localmake(a, b, scope)),
	"thing": (1, lambda scope, n: scope[n.lower()]),
	
	"if": (2, lambda scope, a, b: do_if(a, b, scope)),
	"ifelse": (3, lambda scope, a, b, c: do_ifelse(a, b, c, scope)),
	"test": (1, lambda scope, code: do_test(code, scope)),
	"iftrue": (1, lambda scope, code: do_iftrue(code, scope)),
	"iffalse": (1, lambda scope, code: do_iffalse(code, scope)),
	
	# The condition must be a literal list.
	"while": (2, lambda scope, a, b: do_while(parse(a), b, scope)),
	"for": (5, lambda scope, v, f, t, s, c: do_for(v, f, t, s, c, scope)),
	"foreach": (3, lambda scope, v, i, c: do_foreach(v, i, c, scope)),
	
	"fn": (2, lambda scope, args, code: fn(args, code, scope)),
	"function": (3, lambda scope, n, a, c: function(n, a, c, scope)),
	"apply": (2, lambda scope, f, a: f(a)),
	"map": (2, lambda scope, f, a: do_map(f, a)),
	"filter": (2, lambda scope, f, a: do_filter(f, a)),
	"arity": (1, lambda scope, f: len(f.arglist)),
	
	"add": (2, lambda scope, a, b: a + b),
	"sub": (2, lambda scope, a, b: a - b),
	"mul": (2, lambda scope, a, b: a * b),
	"div": (2, lambda scope, a, b: a / b),
	"mod": (2, lambda scope, a, b: a % b),
	"pow": (2, lambda scope, a, b: a ** b),
	"minus": (1, lambda scope, n: - n),
	"abs": (1, lambda scope, n: abs(n)),
	"int": (1, lambda scope, n: math.trunc(n)),
	
	"pi": (0, lambda scope: math.pi),
	"sqrt": (1, lambda scope, n: math.sqrt(n)),
	"sin": (1, lambda scope, n: math.sin(n)),
	"cos": (1, lambda scope, n: math.cos(n)),
	"rad": (1, lambda scope, n: math.radians(n)),
	"deg": (1, lambda scope, n: math.degrees(n)),
	"hypot": (2, lambda scope, a, b: math.hypot(a, b)),

	"min": (2, lambda scope, a, b: min(a, b)),
	"max": (2, lambda scope, a, b: max(a, b)),
	
	"lte": (2, lambda scope, a, b: a <= b),
	"lt": (2, lambda scope, a, b: a < b),
	"eq": (2, lambda scope, a, b: a == b),
	"neq": (2, lambda scope, a, b: a != b),
	"gt": (2, lambda scope, a, b: a > b),
	"gte": (2, lambda scope, a, b: a >= b),
	
	"and": (2, lambda scope, a, b: a and b),
	"or": (2, lambda scope, a, b: a or b),
	"not": (1, lambda scope, cond: not cond),
	
	"first": (1, lambda scope, seq: seq[0]),
	"last": (1, lambda scope, seq: seq[-1]),
	"butfirst": (1, lambda scope, seq: seq[1:]),
	"butlast": (1, lambda scope, seq: seq[:-1]),
	"count": (1, lambda scope, seq: len(seq)),
	"sorted": (1, lambda scope, seq: sorted(seq)),
	
	"list": (2, lambda scope, a, b: [a, b]),
	"fput": (2, lambda scope, a, b: [a] + b),
	"lput": (2, lambda scope, a, b: b + [a]),
	"item": (2, lambda scope, a, b: b[a]),
	"iseq": (2, lambda scope, a, b: iseq(a, b)),
	
	"concat": (2, lambda scope, a, b: list(a) + list(b)),
	"slice": (3, lambda scope, a, b, seq: seq[a:b]),
	"setitem": (3, lambda scope, i, seq, v: setitem(i, seq, v)),
	
	"lowercase": (1, lambda scope, s: s.lower()),
	"uppercase": (1, lambda scope, s: s.upper()),
	"trim": (1, lambda scope, s: s.strip()),
	"ltrim": (1, lambda scope, s: s.lstrip()),
	"rtrim": (1, lambda scope, s: s.rstrip()),
	
	"empty": (0, lambda scope: ""),
	"space": (0, lambda scope: " "),
	"tab": (0, lambda scope: "\t"),
	"nl": (0, lambda scope: "\n"),

	"split": (1, lambda scope, s: s.split()),
	"join": (1, lambda scope, seq: " ".join(seq)),
	"split-by": (2, lambda scope, sep, s: s.split(sep)),
	"join-by": (2, lambda scope, s, seq: s.join(seq)),
	"word": (2, lambda scope, a, b: str(a) + str(b)),
	
	"starts-with": (2, lambda scope, a, b: b.startswith(a)),
	"ends-with": (2, lambda scope, a, b: b.endswith(a)),

	"to-string": (1, lambda scope, n: str(n)),
	"parse-int": (1, lambda scope, s: int(s)),
	"parse-float": (1, lambda scope, s: float(s)),
	
	"is-string": (1, lambda scope, n: type(n) == str),
	"is-bool": (1, lambda scope, n: type(n) == bool),
	"is-int": (1, lambda scope, n: type(n) == int),
	"is-float": (1, lambda scope, n: type(n) == float),
	"is-list": (1, lambda scope, n: type(n) == list),
	"is-dict": (1, lambda scope, n: type(n) == dict),
	"is-fn": (1, lambda scope, n: isinstance(n, Closure)),
	"is-proc": (1, lambda scope, n: n in procedures.values()),

	"is-space": (1, lambda scope, n: type(n) == str and n.isspace()),
	"is-alpha": (1, lambda scope, n: type(n) == str and n.isalpha()),
	"is-alnum": (1, lambda scope, n: type(n) == str and n.isalnum()),
	"is-digit": (1, lambda scope, n: type(n) == str and n.isdigit()),
	
	"dict": (1, lambda scope, init: do_dict(init)),
	"get": (2, lambda scope, d, k: d[k]),
	"put": (3, lambda scope, d, k, v: put(d, k, v)),
	"del": (2, lambda scope, d, k: do_del(d, k)),
	"keys": (1, lambda scope, d: d.keys()),
	
	"rnd": (0, lambda scope: random.random()),
	"random": (2, lambda scope, a, b: random.randint(a, b)),
	"rerandom": (1, lambda scope, n: random.seed(n)),
	"pick": (1, lambda scope, n: random.choice(n)),
	
	"timer": (0, lambda scope: time.process_time())
}

if __name__ == "__main__":
	import sys
	
	if len(sys.argv) > 1:
		toplevel = Scope()
		try:
			for i in results(parse(sys.argv[1:]), toplevel):
				if i != None:
					print(i)
		except Exception as e:
			print(e, file=sys.stderr)
	else:
		print("Lunar Logo alpha release, 2017-01-29")
		print("Usage:\n\tlunar.py [logo code...]")
		print("\tlunar.py load <filename>")
