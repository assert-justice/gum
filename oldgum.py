# GUM BUILD SYSTEM
# Version 0.0.1
import sys, os, shutil, toml, subprocess
def valid_name(name):
    return True

dirmap_template = {
    "src":{"main.c":""},
    "bin":{
        "debug":{},
        "release":{}
    },
    "include":{},
    "libs":{},
    "gum.toml":""
}
def execute_dirmap(dirmap, direc):
    for node in dirmap:
        val = dirmap[node]
        valtype = type(val)
        path = os.path.join(direc, node)
        if valtype == type(""):
            # create file
            if not os.path.exists(path) or os.path.isfile(path):
                f = open(path, "w")
                f.close()
            else:
                print("cannot create file at", path)
        elif valtype == type({}):
            # create directory and call itself
            if not os.path.exists(path):
                # add it
                os.mkdir(path)
                pass
            elif os.path.isdir(path):
                # overwrite it
                shutil.rmtree(path)
                os.mkdir(path)
                pass
            else:
                print("cannot create directory at", path)
                return
            execute_dirmap(val, path)
        else:
            # problem
            pass

def create(args):
    # validate name
    if len(args) < 1:
        print("create requires a project name")
        return
    name = args[0]
    if not valid_name(name):
        print("invalid name '" + name + "'")
        return
    language = "c"
    if len(args) > 1:
        language = args[1]
        if not language in ["c", "cpp"]:
            print("language '" + language + "' is not supported")
            return
    # create directory
    direc = os.getcwd()
    dirmap = {name: dirmap_template}
    execute_dirmap(dirmap, direc)
    # git init
    # create toml template
    # add main.c

def grab_files(path, suffix):
    nodes = os.listdir(path)
    files = []
    for node in nodes:
        npath = os.path.join(path, node)
        if os.path.isfile(npath):
            if node[-len(suffix):] == suffix:
                files.append(npath)
        else:
            files += grab_files(npath, suffix)
    return files

def build(args):
    root = os.getcwd()
    path = os.path.join(root, "gum.toml")
    if not os.path.exists(path) or not os.path.isfile(path):
        print("cannot locate gum.toml at ", path)
        return
    conf_file = open(path)
    config = toml.load(conf_file)
    path = os.path.join(root, "src")
    files = grab_files(path, "c")
    compiler = config["defaults"]["compiler"]
    name = config["name"]
    dest = os.path.join(root, "bin", "debug", name + ".exe")
    command = [compiler, "-o", name] + files
    subprocess.run(command)

def add(args):
    if len(args) < 1:
        print("missing path to files")
    dest = args[0]
    dest = dest.split("/")
    path = os.getcwd()
    for dir in dest[:-1]:
        path = os.path.join(path, dir)
        if not os.path.exists(path) or os.path.isdir(path):
            continue
        print("cannot find or create directory at", path)

def main():
    args = sys.argv
    if len(args) == 1:
        print("not enough arguments")
        return
    op = args[1]
    if op == "create":
        create(args[2:])
        pass
    elif op == "build":
        build(args[2:])
        pass
    elif op == "run":
        pass
    elif op == "add":
        pass

if __name__ == "__main__":
    main()