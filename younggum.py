import sys, os, shutil, toml, subprocess

__version__ = "0.0.1"

class Gum():
    def __init__(self) -> None:
        self.cwd = os.getcwd()
        args = sys.argv
        self.args = args
        self.gumdir = os.path.split(args[0])[0]
        if len(args) == 1:
            self.version()
            self.help()
            return
        self.dirmap = {
            "src":{"main.c":""},
            "bin":{
                "debug":{},
                "release":{}
            },
            "include":{},
            "libs":{},
            "deps":{},
            "gum.toml":"",
            ".gitignore":""
        }
        self.templates = {
            "gum.toml": self.format_config,
        }
        command = args[1]
        if command == "create":
            # create new project
            self.create()
            return
        commands = {
            "build": self.build,
            "run": self.run,
            "script": self.script,
            "deps": self.build_deps
        }
        if not command in commands:
            # error, unrecognized command
            self.error(f"unrecognized command '{command}'")
        # validate project structure

        # grab config toml
        self.config = self.get_config()
        commands[command]()
    def error(self, message):
        print(message)
        sys.exit(1)
    def version(self):
        print(f"Gum Version {__version__}")
    def help(self):
        print("gum usage:")
    def validate_name(self, name):
        return True
    def validate_structure(self):
        return True
    def list_dir(self, path):
        dirs = []
        files = []
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_dir():
                    dirs.append(entry)
                elif entry.is_file():
                    files.append(entry)
        return dirs, files
    def walk_dirmap(self, func, dirmap = None, path = None):
        if dirmap == None:
            dirmap = self.dirmap
        if path == None:
            path = self.cwd
        dirs, files = self.list_dir(path)
        func(path, dirmap, dirs, files)
        dirmap_dirs = [key for key in dirmap if dirmap[key] != ""]
        for d in dirmap_dirs:
            self.walk_dirmap(func, dirmap[d], os.path.join(path, d))
    def get_templates(self):
        my_path = os.path.join(self.gumdir, "templates")
        _, files = self.list_dir(my_path)
        templates = {}
        for file in files:
            with open(file.path) as f:
                templates[file.name] = f.read()
        self.templates = templates
        return templates
    def create(self):
        if len(self.args) < 3:
            self.error("not enough arguments provided to 'create', requires a project name")
        self.name = self.args[2]
        self.validate_name(self.name)
        # create config toml
        # create directories & file templates
        self.get_templates()
        def setup(path, dirmap, _, __):
            for key in dirmap:
                val = dirmap[key]
                if val == "":
                    if key in self.templates:
                        text = self.templates[key]
                        if key == "gum.toml":
                            text = text.format(f"'{self.name}'", "'gcc'", "'c'")
                        with open(os.path.join(path, key), "w") as f:
                            f.write(text)
                    continue
                temp = os.path.join(path, key)
                if os.path.exists(temp):
                    shutil.rmtree(temp)
                os.mkdir(temp)
        #os.mkdir(self.name)
        # path = os.path.join(self.cwd, self.name)
        # if os.path.isdir(path):
        #     shutil.rmtree(path)
        # os.mkdir(path)
        self.walk_dirmap(setup, {self.name: self.dirmap})
        pass
    def format_config(self):
        pass
    def get_config(self):
        data = toml.load(os.path.join(self.cwd, "gum.toml"))
        config = data["defaults"]
        target = data["debug"]
        config["options"] += target["options"]
        config["dest"] = os.path.join(self.cwd, "bin", "debug", data["name"])
        if "compiler" in target:
            config["compiler"] = target
        return config
    def get_files(self, path, suffix):
        s_files = []
        for root, _, files in os.walk(path):
            for file in files:
                if file[-len(suffix):] == suffix:
                    s_files.append(os.path.join(root, file))
        return s_files
    def build(self):
        config = self.get_config()
        s_files = self.get_files(os.path.join(self.cwd, "src"), config["language"])
        command = []
        #command = [config["compiler"], "-o", config["dest"]] + s_files
        command.append(config["compiler"])
        command += config["options"]
        command += ["-o", config["dest"]] + s_files
        subprocess.run(command)
        return config["dest"]
    def run(self):
        dest = self.build()
        subprocess.run([dest])
        pass
    def build_deps(self):
        path = os.path.join(self.cwd, "deps")
        libspath = os.path.join(self.cwd, "libs")
        dirs, _ = self.list_dir(path)
        conf = self.config
        for dir in dirs:
            temp_path = os.path.join(dir.path, "temp")
            libname = "lib" + dir.name + ".a"
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path)
            os.mkdir(temp_path)
            s_files = self.get_files(dir.path, "c")
            o_files = []
            for file in s_files:
                fname = os.path.split(file)[1]
                fname = fname.split(".")[0]
                fname = os.path.join(temp_path, fname)
                o_files.append(fname)
                command = [conf["compiler"], "-Wall", "-Wextra", "-o", fname, "-c", file]
                print(command)
                subprocess.run(command)
            libpath = os.path.join(libspath, libname)
            command = ["ar", "cr", libpath] + o_files
            subprocess.run(command)
            shutil.rmtree(temp_path)

    def script(self):
        pass

if __name__ == "__main__":
    gum = Gum()
    # path = sys.argv[0]
    # os.path.join(path, "default.toml")
    # f = open("default.toml")
    # spam = f.read()
    # spam = toml.load(spam)
    # f.close()
    # print(spam)