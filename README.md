# Compiler

This Compiler compiles ~~python in python~~ ~~c++ in python~~ ~~c in c~~ c in python into my own custom assembly (for [Excpute](https://github.com/LightslicerGP/Excpute)), with JSON files for intermediate steps.

(currently a WIP, this is like my 4th attempt :sob:)

check the `Compiler.py` code to see what to run, in my case its `python Compiler.py Sample.c --debug`

## Parsing Support

(parsing wise)

- [x] int print() {}
- [ ] int print(int x) {}
- [x] int x = 10;
- [x] int x, y;
- [x] int x = 10, y;
- [x] if () {}
- [x] else {}
- [x] while () {}
- [x] do {} while ()
- [ ] for () {}
- [ ] switch () {}
- [x] struct Point {
      int x;
      int y;
      };
- [ ] struct Point {
      int x;
      int y;
      } pointA, pointB;

## Lexing support

- [x] \0 (End Of File)
- [x] \n (Newline)
- [x] #
- [x] (
- [x] )
- [x] {
- [x] }
- [x] [
- [x] ]
- [x] ,
- [x] :
- [x] ;
- [x] .
- [x] +=
- [x] ++
- [x] -
- [x] -=
- [x] --
- [x] -
- [x] \*=
- [x] -
- [x] > =
- [x] >
- [x] <=
- [x] <
- [x] ==
- [x] =
- [x] !=
- [x] !
- [x] ||
- [x] |
- [x] &&
- [x] &
- [x] ?
- [x] // (Comment)
- [x] /
- [x] "" (String)
- [x] (Space)
- [x] 1234567890 (Decimal Numbers)
- [x] 0x123456789abcdef (Hexadecimal Numbers)
- [x] [char, const, double, enum, float, int, long, short, signed, struct, union, unsigned, void, volatile] (Types)
- [x] [break, case, continue, default, do, else, extern, for, goto, if, register, return, sizeof, static, switch, typedef, while] (Keywords)
