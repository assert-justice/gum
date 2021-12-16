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
optimization = "O0"

[release]
optimization = "O2"
'''

def gitignore():
    return '''.gitignore
/bin/debug/*
/bin/release/*
/libs/*
'''

def c_main(name, time):
    return f'''#include <stdio.h>
// {name}
// created at: {time}
int main(){{
    printf("hello world!");
    return 0;
}}'''