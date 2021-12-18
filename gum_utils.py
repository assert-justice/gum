import os,sys,platform,json
import gum_config

def grab_files(path, extension):
    # Find all files with a given extension in a subtree and return their paths.
    out = []
    for root, _, files in os.walk(path):
        for file in files:
            if file[-len(extension):] == extension:
                out.append(os.path.join(root, file))
    return out

def list_dir(path):
    # List all files and directories at a given path.
    dirs = []
    files = []
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir():
                dirs.append(entry)
            elif entry.is_file():
                files.append(entry)
    return dirs, files

def get_gumpath():
    h, _ = os.path.split(sys.argv[0])
    return h

def get_os():
    lookup = {"Windows":"win"}
    val = platform.system()
    if val in lookup:
        return lookup[val]

def walk_dirmap(dirmap, path, create = False, templates = None):
    # Walk a file structure. If create is true it will create directories and templates as needed.
    # If false and a directory or file is not found will throw error.
    if not templates:
        templates = {}
    if create:
        os.mkdir(path)
    for key, value in dirmap.items():
        p = os.path.join(path, key)
        if not create:
            if not os.path.exists(p):
                error(f"path '{path}' does not exist")
            continue
        if isinstance(value, str):
            txt = value
            if value in templates:
                txt = templates[value]()
            with open(p, "w") as f:
                f.write(txt)
        else:
            walk_dirmap(value, p, create, templates)

def error(message):
    # Displays error messages and quits.
    print(f"Error: {message}")
    sys.exit(2)

def confirm(message):
    # Asks the user a question and expects input. y or Y for yes, n or N for no. If neither asks again.
    while True:
        inp = input(f"{message} (y/n)  ").lower().strip()
        if inp == "y":
            return True
        elif inp == "f":
            return False
        else:
            print("Please enter 'y' or 'n' for your answer.")

def option(message, options):
    # Asks the user to pick from a set of options and returns that option. If input is invalid ask again.
    while True:
        inp = input(f"{message}: {str(options)}").lower().strip()
        if inp in options:
            return inp
        print("Please enter a valid option.")

def split_path(path):
    out = []
    head, path = os.path.splitdrive(path)
    while True:
        path, tail = os.path.split(path)
        out.append(tail)
        #print(path, head)
        if len(path) == 1:
            out.append(head)
            return list(reversed(out))

def write_prep(path, fname = None):
    dirs = split_path(path)
    path = dirs.pop(0) 
    path += os.path.sep
    for dir in dirs:
        path = os.path.join(path, dir)
        if not os.path.exists(path):
            os.mkdir(path)
        elif not os.path.isdir(path):
            error(f"Path '{path}' exists but is not a directory.")
    if fname:
        path = os.path.join(path, fname)
        if os.path.exists(path):
            if os.path.isfile(path):
                return confirm(f"File at path '{path}' already exists! Overwite it?")
            error(f"Path '{path}' exists but is not a file.")
    return True

def config_build(src, release_mode = False, target = "gnu"):
    def add(src, dest):
        for k,v in src.items():
            if k in dest and isinstance(dest[k], list):
                dest[k] += v
            else:
                dest[k] = v
    config = {}
    add_queue = []
    if "defaults" in src:
        add_queue.append(src.pop("defaults"))
    oss = gum_config.targets
    for o in oss:
        if o in src:
            val = src.pop(o)
            if o == target:
                add_queue.append(val)
    modes = ["debug", "release"]
    mode = "release" if release_mode else "debug"
    for m in modes:
        if m in src:
            val = src.pop(m)
            if m == mode:
                add_queue.append(val)
    add(src, config)
    add_queue = list(map(lambda d: config_build(d, release_mode, target), add_queue))
    for d in add_queue:
        add(d, config)
    return config
