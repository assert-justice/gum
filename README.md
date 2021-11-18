# GUM Build System
A bad build system that no one should use.
I made GUM because CMake is very complicated and ad-hoc and I was too stubborn to learn something else.

## Commands
`create [name] (-cpp)`: create a new gum project. It creates a directory with the name specified, creates subdirectories, adds main.c and gum.toml.

`build (-release) (-full) (-libs)`: compile an executable for the current platform

`run`: like build but runs the executable afterwards assuming no errors or warnings

`add [name]`: adds a matching header / source file at `src/name`