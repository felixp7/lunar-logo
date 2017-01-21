#!/usr/bin/env python3

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
	
	def __getitem__(self, key):
		#key = key.lower()
		if key in self.names:
			return self.names[key]
		elif self.parent != None:
			return self.parent[key]
		else:
			raise KeyError("Undefined variable: " + str(key))
	
	def __setitem__(self, key, value):
		key = key.lower()
		if key in self.names:
			self.names[key] = value
		elif self.parent != None:
			self.parent[key] = value
		else:
			#raise KeyError("Undefined variable: " + str(key))
			self.names[key] = value

def parse(words):
	code = []
	buf = None
	in_list = False
	for i in words:
		if in_list == True:
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
			elif len(i) > 1:
				buf = []
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
		elif i in procedures:
			code.append(procedures[i])
		elif i.isdigit():
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

def eval_next(code, cursor, scope):
	value = code[cursor]
	if type(value) == tuple:
		cursor += 1
		args = []
		for i in range(value[0]):
			if cursor >= len(code):
				raise SyntaxError(
					"Unexpected end of input in eval.")
			tmp, cursor = eval_next(code, cursor, scope)
			args.append(tmp)
		return value[1](scope, *args), cursor
	elif type(value) != str:
		return value, cursor + 1
	elif value[0] == ":":
		name = value[1:]
		return scope[name], cursor + 1
	elif value == "do":
		return scan_block(code, cursor + 1)
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
def run(code, scope):
	cursor = 0
	while cursor < len(code):
		value, cursor = eval_next(code, cursor, scope)
		if scope.continuing:
			scope.continuing = False
			return None
		elif scope.breaking:
			return None
		elif scope.returning:
			return value
		elif value != None:
			raise ValueError(
				"You don't say what to do with: "
					+ str(value))

def results(code, scope):
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

# Printing out.
def do_print(value):
	if type(value) == list:
		return print(" ".join(value))
	else:
		return print(value)

def do_type(value):
	if type(value) == list:
		return print(" ".join(value), end='')
	else:
		return print(value, end='')

# Creating variables.
def make(varname, value, scope):
	scope[varname] = value

def local(varname, scope):
	if type(varname) == list:
		for i in varname:
			scope.names[i.lower()] = None
	else:
		scope.names[varname.lower()] = None

# Conditionals.
def do_if(cond, code, scope):
	if cond: run(code, scope)

def do_ifelse(cond, ift, iff, scope):
	if cond:
		return run(parse(ift), scope)
	else:
		return run(parse(iff), scope)

def do_test(cond, scope):
	scope.test = cond

def do_iftrue(code, scope):
	if scope.test:
		run(code, scope)

def do_iffalse(code, scope):
	if not scope.test:
		run(code, scope)

# Loops.
def do_while(cond, code, scope):
	cond = parse(cond)
	while run(cond, scope):
		value = run(code, scope)
		if scope.returning:
			return value
		elif scope.breaking:
			scope.breaking = False
			break

def do_for(varname, init, limit, step, code, scope):
	make(varname, init, scope)
	if limit >= init:
		while scope[varname] <= limit:
			value = run(code, scope)
			if scope.returning:
				return value
			elif scope.breaking:
				scope.breaking = False
				break
			scope[varname] += step
	else:
		while scope[varname] >= limit:
			value = run(code, scope)
			if scope.returning:
				return value
			elif scope.breaking:
				scope.breaking = False
				break
			scope[varname] += step

def do_foreach(varname, items, code, scope):
	for i in items:
		make(varname, i, scope)
		value = run(code, scope)
		if scope.returning:
			return value
		elif scope.breaking:
			scope.breaking = False
			break

# Lists.
def iseq(init, limit):
	if init <= limit:
		return list(range(init, limit + 1))
	else:
		return list(range(init, limit - 1, -1))

procedures = {
	"parse": (1, lambda scope, code: parse(code)),
	"run": (1, lambda scope, code: run(code, scope)),
	"results": (1, lambda scope, code: results(code, scope)),
	"load": (1, lambda scope, f: load(f, scope)),
	"ignore": (1, lambda scope, value: None),
	
	"break": (0, lambda scope: do_break(scope)),
	"continue": (0, lambda scope: do_continue(scope)),
	"return": (1, lambda scope, value: do_return(value, scope)),

	"print": (1, lambda scope, item: do_print(item)),
	"type": (1, lambda scope, item: do_type(item)),
	"show": (1, lambda scope, item: print(item)),
	
	"readline": (0, lambda scope: input().split()),
	"readword": (0, lambda scope: input()),

	"make": (2, lambda scope, a, b: make(a, b, scope)),
	"name": (2, lambda scope, a, b: make(b, a, scope)),
	"local": (1, lambda scope, n: local(n, scope)),
	
	"if": (2, lambda scope, a, b: do_if(a, b, scope)),
	"ifelse": (3, lambda scope, a, b, c: do_ifelse(a, b, c, scope)),
	"test": (1, lambda scope, code: do_test(code, scope)),
	"iftrue": (1, lambda scope, code: do_iftrue(code, scope)),
	"iffalse": (1, lambda scope, code: do_iffalse(code, scope)),
	
	"while": (2, lambda scope, a, b: do_while(a, b, scope)),
	"for": (5, lambda scope, v, f, t, s, c: do_for(v, f, t, s, c, scope)),
	"foreach": (3, lambda scope, v, i, c: do_foreach(v, i, c, scope)),
	
	"add": (2, lambda scope, a, b: a + b),
	"sub": (2, lambda scope, a, b: a - b),
	"mul": (2, lambda scope, a, b: a * b),
	"div": (2, lambda scope, a, b: a / b),
	"mod": (2, lambda scope, a, b: a % b),
	"pow": (2, lambda scope, a, b: a ** b),
	"minus": (1, lambda scope, n: - n),
	"abs": (1, lambda scope, n: abs(n)),
	"int": (1, lambda scope, n: int(n)),
	
	"sqrt": (1, lambda scope, n: math.sqrt(n)),
	"sin": (1, lambda scope, n: math.sin(n)),
	"cos": (1, lambda scope, n: math.cos(n)),
	
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
	"iseq": (2, lambda scope, a, b: iseq(a, b)),
	
	"rnd": (0, lambda scope: random.random()),
	"random": (2, lambda scope, a, b: random.randint(a, b)),
	"rerandom": (1, lambda scope, n: random.seed(n)),
	
	"timer": (0, lambda scope: time.process_time())
}

if __name__ == "__main__":
	import sys
	
	toplevel = Scope()
	#print(parse(sys.argv[1:]))
	for i in results(parse(sys.argv[1:]), toplevel):
		print(i)
