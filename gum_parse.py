import argparse
import gum_config

def parse(create, build, run, install, acp, add):
    def compile_parser(parser : argparse.ArgumentParser):
        #parser = subparsers.add_parser("build", aliases=["b"], help="Compile the project as an executable.")
        #parser.set_defaults(func=build)
        parser.add_argument("-r","--release", action="store_true", help="Compile using release settings.")
        #parser.add_argument("-f","--full", action="store_true", help="Recompile all source files, do not use incremental builds.")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--all_libs", action="store_true", help="Recompile all libraries in the deps directory.")
        group.add_argument("--libs", nargs="+", help="Recompile a subset of libraries.")
        parser.add_argument("-s", "--skip", action="store_true", help="Skip compiling the main program. Used to only compile libraries.")
        group = parser.add_mutually_exclusive_group()
        #group.add_argument("-a","--all", action="store_true", help="Compile to all configured targets. Not yet implemented.")
        group.add_argument("-t","--target", choices=gum_config.targets, help="Specify compile target if different than current machine.")
        parser.add_argument("-o", type=int, choices=[0,1,2,3], help="Override the default optimization level.")
        return parser

    parser = argparse.ArgumentParser(prog="gum", description="A bad build system, built out of gum and twine.")
    parser.add_argument("-v", "--version", action="version", version=gum_config.version)
    subparsers = parser.add_subparsers()

    create_parser = subparsers.add_parser("create", aliases=["c"], help="Create a new gum project. It creates a directory with the name specified, builds a directory tree complete with template files, and adds source control.")
    create_parser.set_defaults(func=create)
    create_parser.add_argument("name", help="The name of your new project")
    create_parser.add_argument("-c", "--compiler", choices=gum_config.compilers, default="gcc", help="Specify a compiler for the project's use.")
    create_parser.add_argument("-l", "--language", choices=gum_config.languages, default="c", help="Specify the project's language ('c' and 'c++' are currently supported).")
    create_parser.add_argument("--header", default=".h", help="Specify the file extension used for header files.")
    create_parser.add_argument("--src", default=".c", help="Specify the file extension used for source files.")
    create_parser.add_argument("--vcs", choices=gum_config.vcs, default="git", help="Specify the version control system for the project ('none' and 'git' is currently supported).")

    build_parser = subparsers.add_parser("build", aliases=["b"], help="Compile the project as an executable.")
    build_parser.set_defaults(func=build)
    compile_parser(build_parser)

    run_parser = subparsers.add_parser("run", aliases=["r"], help="Builds and runs the project assuming no errors or warnings. All commands work identically.")
    run_parser.set_defaults(func=run)
    compile_parser(run_parser)

    install_parser = subparsers.add_parser("install", aliases=["i"], help="Clone a library into the deps folder and configure it.")
    install_parser.set_defaults(func=install)
    group = install_parser.add_mutually_exclusive_group()
    group.add_argument("--url", help="Clone from the following url.")
    group.add_argument("--name", help="Create a new library with the given name.")
    #install_parser.add_argument("-d", "--dynamic", action="store_true", help="Configure library as dynamically linked. Static is a default. Not currently implemented all libraries are static.")
    install_parser.add_argument("-m", "--manual", action="store_true", help="Indicates that headers should not be automatically placed in the project's include file. For pesky libraries with specific include instructions.")
    #install_parser.add_argument("--defer", action="store_true", help="Indicates that a library should not be built yet. Default is to build on install.")

    acp_parser = subparsers.add_parser("acp")
    acp_parser.add_argument("message")
    acp_parser.set_defaults(func=acp)

    add_parser = subparsers.add_parser("add", help="Adds a matching header / source file at `src/path/name`")
    add_parser.set_defaults(func=add)
    add_parser.add_argument("path")
    add_parser.add_argument("name")
    add_parser.add_argument("--lib", help="Specifies you want to add the files to the src folder of a library in the deps folder.")
    add_parser.add_argument("--template", help="Specify a template to use when creating the files.")
    args = parser.parse_args()
    out = args.__dict__.copy()
    out.pop("func")
    args.func(out)