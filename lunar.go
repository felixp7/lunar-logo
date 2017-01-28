// Lunar Logo: clean, minimal scripting language based on Logo and Lua.
package main

import (
	"fmt"
	"strings"
	"strconv"
	"regexp"
	"os"
	"bufio"
	"math"
	"time"
)

var Ins = os.Stdin
var Outs = os.Stdout
var Errs = os.Stderr

var intre = regexp.MustCompile(`^-?[[:digit:]]+$`)
var splitre = regexp.MustCompile(`[[:space:]]+`)

type List []interface{}
type Dict map[string]interface{}

type Scope struct {
	Names Dict
	Parent *Scope
	
	continuing bool
	breaking bool
	returning bool
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
	if _, ok := self.Names[name]; ok {
		self.Names[name] = value
	} else if self.Parent != nil {
		self.Parent.Put(name, value)
	} else {
		self.Names[name] = value
	}
}

func (self *Closure) Apply(args ...interface{})  (interface{}, error) {
	locals := Scope{Names: Dict{}, Parent: self.Scope}
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
	return block, cursor + 1, nil
}

func Parse(words []string, context map[string]Builtin) (List, error) {
	code := make([]interface{}, 0, len(words))
	var buf List = nil
	in_list := false
	for _, i := range(words) {
		if len(i) == 0 { continue }
		lower := strings.ToLower(i)
		if in_list {
			if strings.HasSuffix(i, "]") {
				if len(i) > 1 {
					buf = append(buf, i[:len(i) - 1])
				}
				code = append(code, List(buf))
				in_list = false
			} else {
				buf = append(buf, i)
			}
		} else if i == "[]" {
			code = append(code, make(List, 0))
		} else if strings.HasPrefix(i, "[") {
			if strings.HasSuffix(i, "]") {
				code = append(code, List{i[1:len(i) - 1]})
			} else {
				buf = make([]interface{}, 0)
				if len(i) > 1 {
					buf = append(buf, i[1:])
				}
				in_list = true
			}
		} else if strings.HasPrefix(i, "--") {
			break
		} else if strings.HasPrefix(i, ":") {
			code = append(code, lower)
		} else if lower  == "do" || lower == "end" {
			code = append(code, lower)
		} else if lower == "true" {
			code = append(code, true)
		} else if lower == "false" {
			code = append(code, false)
		} else if lower == "nil" {
			code = append(code, nil)
		} else if proc, ok := context[lower]; ok {
			code = append(code, proc)
		} else if intre.MatchString(i) {
			value, err := strconv.Atoi(i)
			if err == nil {
				code = append(code, value)
			} else {
				code = append(code, 0)
			}
		} else {
			value, err := strconv.ParseFloat(i, 64)
			if err == nil {
				code = append(code, value)
			} else {
				code = append(code, i)
			}
		}
	}
	if in_list {
		return List(code), Error{"Unclosed list at end of line."}
	} else {
		return List(code), nil
	}
}

//Underlies most other control structures.
func Run(code List, scope *Scope) (interface{}, error) {
	cursor := 0
	for cursor < len(code) {
		value, csr, err := EvalNext(code, cursor, scope)
		if err != nil {
			return nil, err
		} else if scope.continuing || scope.breaking {
			return nil, nil
		} else if scope.returning {
			return value, nil
		} else if value != nil {
			return value, Error{
				"You don't say what to do with: " +
					fmt.Sprint(value)}
		}
		cursor = csr
	}
	return nil, nil
}

// Underlies while, ifelse and the command line.
func Results(code List, scope *Scope) (List, error) {
	values := make([]interface{}, 0, len(code))
	cursor := 0
	for cursor < len(code) {
		val, csr, err := EvalNext(code, cursor, scope)
		if err != nil {
			return List(values), err
		} else if scope.returning {
			return List{val}, nil
		} else if scope.breaking || scope.continuing {
			break
		}
		values = append(values, val)
		cursor = csr
	}
	return List(values), nil
}

func Load(fn string, ctx map[string]Builtin, s *Scope) (interface{}, error) {
	code := make([]interface{}, 0)
	file, err := os.Open(fn)
	if err != nil { return nil, err }
	defer file.Close()
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		words := splitre.Split(scanner.Text(), -1)
		tokens, err := Parse(words, ctx)
		if err != nil { return nil, err }
		code = append(code, tokens...)
	}
	if scanner.Err() == nil {
		return Run(List(code), s)
	} else {
		return nil, scanner.Err()
	}
}

// For loop; the variable is always treated as local.
func For(v string, i, l, p float64, code List, s *Scope) (interface{}, error) {
	v = strings.ToLower(v)
	s.Names[v] = i
	if l >= i {
		for i <= l {
			value, err := Run(code, s)
			if err != nil {
				return nil, err
			} else if s.returning {
				return value, nil
			} else if s.continuing {
				s.continuing = false
			} else if s.breaking {
				s.breaking = false
				break
			}
			i += p
			s.Names[v] = i
		}
	} else {
		for i >= l {
			value, err := Run(code, s)
			if err != nil {
				return nil, err
			} else if s.returning {
				return value, nil
			} else if s.continuing {
				s.continuing = false
			} else if s.breaking {
				s.breaking = false
				break
			}
			i += p
			s.Names[v] = i
		}
	}
	return nil, nil
}

func ParseFloat(input interface{}) float64 {
	switch input := input.(type) {
		case float64: return float64(input)
		case int: return float64(input)
		case string:
			value, err := strconv.ParseFloat(input, 64)
			if err == nil {
				return value
			} else {
				return math.NaN()
			}
		default: return math.NaN()
	}
}

var Procedures = map[string]Builtin {
	"run": {1, func (s *Scope, a ...interface{}) (interface{}, error) {
		if code, ok := a[0].(List); ok {
			return Run(code, s)
		} else {
			return nil, Error{
				"Run expects a list, found: " +
				fmt.Sprint(a[0])}
		}
	}},
	"results": {1, func (s *Scope, a ...interface{}) (interface{}, error) {
		if code, ok := a[0].(List); ok {
			return Results(code, s)
		} else {
			return nil, Error{
				"Results expects a list, found: " +
				fmt.Sprint(a[0])}
		}
	}},
	
	"print": {1, func (s *Scope, a ...interface{}) (interface{}, error) {
		fmt.Fprintln(Outs, a[0])
		return nil, nil
	}},
	
	"make": {2, func (s *Scope, a ...interface{}) (interface{}, error) {
		if varname, ok := a[0].(string); ok {
			s.Put(strings.ToLower(varname), a[1])
			return nil, nil
		} else {
			return nil, Error{
				"Varname should be string in make, found: " +
				fmt.Sprint(a[0])}
		}
	}},
	
	"for": {5, func (s *Scope, a ...interface{}) (interface{}, error) {
		varname := a[0].(string)
		init := ParseFloat(a[1])
		limit := ParseFloat(a[2])
		step := ParseFloat(a[3])
		code := a[4].(List)
		return For(varname, init, limit, step, code, s)
	}},
	"add": {2, func (s *Scope, a ...interface{}) (interface{}, error) {
		switch t1 := a[0].(type) {
		case int:
			switch t2 := a[1].(type) {
				case int: return t1 + t2, nil
				case float64: return float64(t1) + t2, nil
				default: return math.NaN(), nil
			}
		case float64:
			switch t2 := a[1].(type) {
				case int: return t1 + float64(t2), nil
				case float64: return t1 + t2, nil
				default: return math.NaN(), nil
			}
		default:
			return math.NaN(), nil
		}
	}},
	"sub": {2, func (s *Scope, a ...interface{}) (interface{}, error) {
		switch t1 := a[0].(type) {
		case int:
			switch t2 := a[1].(type) {
				case int: return t1 - t2, nil
				case float64: return float64(t1) - t2, nil
				default: return math.NaN(), nil
			}
		case float64:
			switch t2 := a[1].(type) {
				case int: return t1 - float64(t2), nil
				case float64: return t1 - t2, nil
				default: return math.NaN(), nil
			}
		default:
			return math.NaN(), nil
		}
	}},
	"div": {2, func (s *Scope, a ...interface{}) (interface{}, error) {
		return ParseFloat(a[0]) / ParseFloat(a[1]), nil
	}},

	"timer": {0, func (s *Scope, a ...interface{}) (interface{}, error) {
		return float64(
			time.Now().UnixNano()) / (1000 * 1000 * 1000), nil
	}},
}

func init() {
	tmp := func (s *Scope, a ...interface{}) (interface{}, error) {
		if filename, ok := a[0].(string); ok {
			return Load(filename, Procedures, s)
		} else {
			return nil, Error{
				"Filename should be string in load, found: " +
				fmt.Sprint(a[0])}
		}
	}
	Procedures["load"] = Builtin{1,	tmp}
}

func main() {
	if len(os.Args) > 1 {
		toplevel := Scope{Names: Dict{}}
		code, err := Parse(os.Args[1:], Procedures)
		if err == nil {
			results, err2 := Results(code, &toplevel)
			if err2 == nil {
				for _, i := range(results) {
					if i != nil {
						fmt.Println(i)
					}
				}
			} else {
				fmt.Fprintln(Errs, err2)
			}
		} else {
			fmt.Fprintln(Errs, err)
		} 
	} else {
		fmt.Println("Lunar Logo alpha release, 2017-01-28")
		fmt.Println("Usage:\n\tlunar.py [logo code...]")
		fmt.Println("\tlunar.py load <filename>")
	}
}
