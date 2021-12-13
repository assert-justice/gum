# GUM Build System
A bad build system that no one should use.
I made GUM because CMake is very complicated and ad-hoc and I was too stubborn to learn something else.

## Commands

### Create

`create [name]`: create a new gum project. It creates a directory with the name specified, creates subdirectories, adds main.c and gum.toml.

- `-c --compiler [str]`: specify a compiler for the project's use.

- `-l --language [str]`: specify the project's language (`c` and `c++` are currently supported).

- `-h --head [str]`: specify the file extension used for header files.

- `-s -- src [str]`: specify the file extension used for source files.

- `--vcs [str]`: specify the version control system for the project (`git` is currently supported).

### Build

`build`: compile an executable for the current platform

- `-r -release`: compile using release settings.

- `-f --full`: recompile all source files, do not use incremental builds.

- `-compile_libs`: recompile all libraries in the deps directory.

- `-a -all_targets`: compile to all configured targets. Not yet implemented.

- `--win --posx --gnu`: specify compile target if different than current machine. Not yet implemented.

- `-o`: override default optimization level.

### Run

`run`: like build but runs the executable afterwards assuming no errors or warnings. All commands work identically.

### Install

`install [url]`: clone a library into the deps folder and configure it.

- `-d -dll`: configure library to be used as a dll. Static is a default.

- `-m --manual`: headers should not be automatically placed in the project's include file. For pesky libraries with specific include instructions.

- `--defer_build`: do not build on install.

### Add Commit Push

`acp [str]`: adds all changes, commits them with the given message, and pushes it to configured repo.

### Script

`script `

`add [name]`: adds a matching header / source file at `src/name`