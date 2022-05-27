# GUM Build System
A bad build system that no one should use.
I made GUM because CMake is very complicated and ad-hoc and I was too stubborn to learn something else.

## Commands

### Create

`create [name]`: Create a new gum project. It creates a directory with the name specified, builds a directory tree complete with template files, and adds source control.

- `-c --compiler [str]`: Specify a compiler for the project's use.

- `-l --language [str]`: Specify the project's language (`c` and `c++` are currently supported).

- `-h --head [str]`: Specify the file extension used for header files.

- `-s -- src [str]`: Specify the file extension used for source files.

- `--vcs [str]`: Specify the version control system for the project (`none` and `git` is currently supported).

### Build

`build`: Compile the project as an executable.

- `-r -release`: Compile using release settings.

- `-f --full`: Recompile all source files, do not use incremental builds. Not yet implemented, all builds are full builds.

- `--all_libs`: Recompile all libraries in the deps directory.

- `--libs [name*]`: Recompile a subset of libraries.

- `-s --skip`: Skip compiling the main program. Used to only compile libraries.

- `-a --all_targets`: Compile to all configured targets. Not yet implemented.

- `--win --posx --gnu`: Specify compile target if different than current machine. Not yet implemented.

- `-o`: Override the default optimization level.

### Run

`run`: Builds and runs the project assuming no errors or warnings. All commands work identically to build.

### Install

`install`: Add a library to the deps folder and configure it.

- `--url [url]`: Clone from the following url. Not yet implemented.

- `--name [name]`: Create a new library with the given name.

- `-d -dll`: Configure library as dynamically linked. Static is a default. Not currently implemented all libraries are static.

- `-m --manual`: Indicates that headers should not be automatically placed in the project's include file. For pesky libraries with specific include instructions.

- `--defer_build`: Indicates that a library should not be built yet. Default is to build on install. Not currently implemented, gum will not build libraries until told to do so explicitly.

### Add Commit Push

`acp [str]`: adds all changes, commits them with the given message, and pushes it to configured repo.

### Add

`add [name]`: adds a matching header / source file at `src/name`