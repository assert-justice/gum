def config(name, compiler, language, header, src):
    return f'''# build script
name = "{name}"
version = "0.0.1"

[defaults]
compiler = "{compiler}"
language = "{language}"
header = "{header}"
src = "{src}"
options = ["-Wall", "-Wextra"]

[debug]
optimization = "-O0"

[release]
optimization = "-O2"
'''

def readme(name):
    return f'''# {name}
'''

def gitignore():
    return '''
*.exe
*.a
*.o
*.s
*.lib
include/*
.vscode/
'''

def c_main(name, time):
    return f'''// {name}
// created at: {time}

#include <stdio.h>
int main(int argc, char* argv[]){{
    printf("hello world!");
    return 0;
}}'''

def c_head(name):
    name = name.upper()
    return f'''#ifndef {name}
#define {name}

#endif
'''

def c_src(name):
    return f'''#include "{name}"

'''