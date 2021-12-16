import os,sys,platform,json

def grab_files(path, extension):
    # Find all files with a given extension in a subtree and return their paths.
    files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file[-len(extension):] == extension:
                files.append(os.path.join(root, file))
    return files

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

def walk_dirmap(templates, dirmap, path, create = False):
    # Walk a file structure. If create is true it will create directories and templates as needed.
    # If false and a directory or file is not found will throw error.
    #dirs, files = list_dir(path)
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
            walk_dirmap(templates, value, p, create)

def error(message):
    # Displays error messages and quits.
    print(f"Error: {message}")
    sys.exit(2)
def confirm(message):
    # Asks the user a question and expects input. y or Y for yes, n or N for no. If neither asks again.
    while True:
        inp = input(f"{message}: y/n\n").lower().strip()
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