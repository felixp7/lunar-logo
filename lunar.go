// Lunar Logo: clean, minimal scripting language based on Logo and Lua.

package lunar

import (
	"fmt"
	"strings"
	"os"
)

var Ins = os.Stdin
var Outs = os.Stdout
var Errs = os.Stderr

type List []interface{}
type Dict map[string]interface{}

type Scope struct {
	Names Dict
	Parent *Scope
}

type Builtin struct {
	Arity int
	Code func (*Scope, ...interface{}) (interface{}, error)
}

type Closure struct {
	Arglist []string
	Code List
	*Scope
}

type Error struct {
	Data interface{}
}

func (self Error) Error() string {
	return fmt.Sprint(self.Data)
}

func (self *Scope) Get(name string) (interface{}, error) {
	if value, ok := self.Names[name]; ok {
		return value, nil
	} else if self.Parent != nil {
		return self.Parent.Get(name)
	} else {
		return nil, Error{"Undefined variable: " + name}
	}
}

func (self *Scope) SafeGet(name string, fallback interface{}) interface{} {
	if value, ok := self.Names[name]; ok {
		return value
	} else if self.Parent != nil {
		return self.Parent.SafeGet(name, fallback)
	} else {
		return fallback
	}
}

func (self *Scope) Put(name string, value interface{}) {
	if value, ok := self.Names[name]; ok {
		self.Names[name] = value
	} else if self.Parent != nil {
		self.Parent.Put(name, value)
	} else {
		self.Names[name] = value
	}
}

func (self *Closure) Apply(args ...interface{})  (interface{}, error) {
	locals := Scope{Dict{}, self.Scope}
	if len(self.Arglist) != len(args) {
		return nil, Error{fmt.Sprintf(
			"%d arguments passed to function expecting %d.",
			len(args), len(self.Arglist))}
	}
	for i, n := range(self.Arglist) {
		locals.Names[n] = args[i]
	}
	return Run(self.Code, &locals)
}

func EvalNext(code List, cursor int, scope *Scope) (interface{}, int, error) {
	collectArgs := func (num int, msg string) (List, error) {
		args := make(List, num)
		for i := 0; i < num; i++ {
			if cursor >= len(code) {
				return args, Error{msg}
			}
			tmp, csr, err := EvalNext(code, cursor, scope)
			if err != nil {
				return args, err
			}
			args[i] = tmp
			cursor = csr
		}
		return args, nil
	}
	
	value := code[cursor]
	
	switch value := value.(type) {
	case Builtin:
		cursor++
		args, err := collectArgs(value.Arity, "Not enough arguments.")
		if err != nil {
			return nil, cursor, err
		}
		tmp, err := value.Code(scope, args...)
		return tmp, cursor, err
	case string:
		if value[0] == ':' {
			// Expect name to be already lowercased.
			tmp, err := scope.Get(value[1:])
			return tmp, cursor + 1, err
		} else if value == "do" {
			return ScanBlock(code, cursor + 1)
		} else {
			closure := scope.SafeGet(
				strings.ToLower(value), value)
			if closure, ok := closure.(Closure); ok {
				cursor++
				args, err := collectArgs(
					len(closure.Arglist),
					"Not enough arguments to " +
						strings.ToLower(value))
				if err != nil {
					return nil, cursor, err
				}
				tmp, err := closure.Apply(args...)
				return tmp, cursor, err
			} else {
				return value, cursor + 1, nil
			}
		}
	default:
		return value, cursor + 1, nil
	}
	return nil, 0, nil
}

func ScanBlock(code List, cursor int) (List, int, error) {
	block := make(List, 0, len(code) - cursor)
	for code[cursor] != "end" {
		if code[cursor] == "do" {
			tmp, csr, err := ScanBlock(code, cursor + 1)
			if err != nil {
				return block, csr, err
			}
			block = append(block, tmp)
			cursor = csr
		} else {
			block = append(block, code[cursor])
			cursor++
		}
		if cursor >= len(code) {
			return block, cursor, Error{
				"Unexpected end of input in block."}
		}
	}
	return block, cursor, nil
}

func Parse(words []string) (List, error) {
	return nil, nil
}

func Run(code List, scope *Scope) (interface{}, error) {
	return nil, nil
}
