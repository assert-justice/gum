import os, subprocess, json, datetime, shutil
import toml
import gum_parse, gum_utils, gum_config, gum_templates

__version__ = gum_config.version

class Gum():
    def __init__(self):
        self.cwd = os.getcwd()
        # Load templates and default config.
        self.load_files()
        # Calls the argument parser.
        gum_parse.parse(self.create, self.build, self.run, self.install, self.acp, self.add)

    def create(self, args):
        # Create a new project
        # Create expected templates
        temps = {
            "config": lambda: gum_templates.config(args["name"], args["compiler"], args["language"], args["header"], args["src"]),
            "gitignore": gum_templates.gitignore,
            "c_main": lambda: gum_templates.c_main(args["name"], datetime.date.today()),
            "readme": lambda: gum_templates.readme(args["name"])
        }
        dirmap = self.dirmaps["create.json"]
        path = os.path.join(self.cwd, args["name"])
        if os.path.exists(path):
            gum_utils.error(f"the project directory '{path}' already exists!")
        gum_utils.walk_dirmap(dirmap, path, True, temps)
        if args["vcs"] == "git":
            subprocess.run("git init".split(), cwd=os.path.join(self.cwd, args["name"]))
    def build(self, args):
        self.prime(args["release"], args["target"])
        # TODO: actually implement scripts, not just this silly hack
        if os.path.exists("scripts/prebuild.py"):
            subprocess.run(["python", "scripts/prebuild.py"])
        config = self.config
        o_level = args.pop('o')
        if o_level:
            config["optimization"] = f"-O{o_level}"
        # options : list = config["options"]
        # options.insert(0, config.pop("optimization"))
        config["options"].append(config.pop("optimization"))
        config["release"] = args["release"]
        if args["all_libs"]:
            if not self.compile_libs():
                return False
        elif args["libs"]:
            if not self.compile_libs(args["libs"]):
                return False
        outname = config["name"]
        if gum_utils.get_os() == "win":
            outname += ".exe"
        dest = os.path.join(self.cwd, "bin", "release" if config["release"] else "debug", outname)
        config["dest"] = dest
        self.config = config
        if args["skip"]:
            return True
        files = gum_utils.grab_files(os.path.join(self.cwd, "src"), config["src"])
        command = [config["compiler"]]
        command += config["options"]
        command.append("-Iinclude")
        command += ["-o", dest] + files
        command.append("-Llibs")
        libfiles = gum_utils.grab_files(os.path.join(self.cwd, "libs"), gum_config.os_lib_extension[config["target"]])
        libfiles += config["libs"]
        command += libfiles #["-l" + file for file in libfiles]
        if "libs" in config:
            command += config["libs"]
        # print(" ".join(command))
        return subprocess.run(command).returncode == 0
    
    def compile_libs(self, names = None):
        deps_path = os.path.join(self.cwd, "deps")
        if not names:
            dirs, _ = gum_utils.list_dir(deps_path)
            names = [dir.name for dir in dirs]
        for name in names:
            d_path = os.path.join(deps_path, name)
            # tries to grab library specific config
            config_path = os.path.join(d_path, "gum_library.toml")
            config = {}
            if os.path.exists(config_path):
                with open(config_path) as f:
                    config = toml.loads(f.read())
            skip_list = []
            if "os_specific" in config:
                for key, lis, in config["os_specific"].items():
                    if key != self.config["target"]:
                        skip_list.extend(lis)
            # get all the source files in the library and compiles them in place into .o files
            files = gum_utils.grab_files(os.path.join(d_path, "src"), self.config["src"])
            # files = gum_utils.grab_files(os.path.join(d_path, "src"), ".cpp")
            src_path = os.path.join(d_path, "src")
            # print(src_path)
            files = [file for file in files if os.path.split(file)[1] not in skip_list]
            # return
            command = [self.config["compiler"],  "-c", f"-I{d_path}/include", f"-I{src_path}"]
            # command = ["g++",  "-c", f"-I{d_path}/include", f"-I{src_path}"]
            command += files
            # print(command)
            if subprocess.run(command, cwd=os.path.join(d_path, "gum")).returncode != 0:
            # if subprocess.run(command, cwd=src_path).returncode != 0:
                return False
            # now we need to find them all
            o_files = gum_utils.grab_files(d_path, ".o")
            # TODO: figure out what other compilers use to link static libraries
            lib_path = os.path.join(self.cwd, "libs", name) + gum_config.os_lib_extension[self.config["target"]]
            command = ["ar", "rs", lib_path] + o_files
            if subprocess.run(command).returncode != 0: # leaves .o files in the gum temporary directory
                return False
            # copy contents of include folder
            # include_path = os.path.join(self.cwd, "include", name)
            # if os.path.exists(include_path):
            #     shutil.rmtree(include_path)
            # shutil.copytree(os.path.join(d_path, "include"), include_path)
        return True

    def run(self, args):
        if self.build(args):
            path, _ = os.path.split(self.config["dest"])
            subprocess.run(self.config["dest"], cwd=path)
    
    def add_src(self, temp, h_path, s_path, name):
        h_ext = self.config["header"]
        s_ext = self.config["src"]
        h_name = f"{name}{h_ext}"
        s_name = f"{name}{s_ext}"
        # TODO: support other templates
        h = gum_templates.c_head(name)
        s = gum_templates.c_src(h_name)
        for path, name, cont in zip((h_path, s_path,), (h_name, s_name,), (h,s,)):
            gum_utils.write_prep(path, name)
            path = os.path.join(path, name)
            with open(path, 'w') as f:
                f.write(cont)
        return h_path, s_path
        

    def install(self, args):
        # print(args)
        self.prime()
        if args["name"]:
            path = os.path.join(self.cwd, "deps", args["name"])
            if os.path.exists(path):
                gum_utils.error(f"Cannot create library at '{path}', directory already exists.")
            gum_utils.walk_dirmap(self.dirmaps["lib.json"], path, True)
            h_path = os.path.join(path, "include")
            s_path = os.path.join(path, "src")
            self.add_src("base", h_path, s_path, args["name"])
            
            if not args["manual"]:
                path = os.path.join(self.cwd, "include", args["name"])
                gum_utils.write_prep(path)
                #os.mkdir(path)
        elif args["url"]:
            pass
        else:
            gum_utils.error("Install requires either a name or url argument.")

    def acp(self, args):
        message = args["message"]
        commands = [
            "git add .",
            f'git commit -m "{message}"',
            "git push"
        ]
        for c in commands:
            subprocess.run(c)

    def add(self, args):
        self.prime()
        # print(args)
        path = args["path"]
        lib = args["lib"]
        name = args["name"]
        if not lib:
            path = os.path.join(self.cwd, "src", path)
        else:
            # TODO: check if lib exists
            path = os.path.join(self.cwd, "deps", lib, "src", path)
        self.add_src("base", path, path, name)
        # name = args["name"]
        # h_ext = self.config["header"]
        # s_ext = self.config["src"]
        # h_name = f"{name}{h_ext}"
        # s_name = f"{name}{s_ext}"
        # h = gum_templates.c_head(name)
        # s = gum_templates.c_src(h_name)
        # if not args["lib"]:
        #     hp = os.path.join(self.cwd, "src", args["path"])
        #     #sp = os.path.join(self.cwd, "src", args["path"])
        #     sp = hp
        # else:
        #     libname = args["lib"]
        #     dirmap = self.dirmaps["lib.json"]
        #     gum_utils.walk_dirmap(dirmap, os.path.join(self.cwd, "deps", libname))
        #     hp = os.path.join(self.cwd, "deps", libname, "src", args["path"])
        #     sp = hp
        #     #sp = os.path.join(self.cwd, "deps", libname, "src", args["path"])
        # if gum_utils.write_prep(hp, h_name) and gum_utils.write_prep(sp, s_name):
        #     pass
        # else:
        #     return
        # hp = os.path.join(hp, h_name)
        # sp = os.path.join(sp, s_name)
        # with open(hp, "w") as h_new:
        #     with open(sp, "w") as s_new:
        #         h_new.write(h)
        #         s_new.write(s)

    def prime(self, release_mode = False, target = None):
        # validate file structure
        # set config field
        if not target:
            target = gum_utils.get_os()
        dirmap = self.dirmaps["validate.json"]
        gum_utils.walk_dirmap(dirmap, self.cwd)
        with open(os.path.join(self.cwd, "gum.toml")) as tom:
            config = toml.load(tom)
            self.config = gum_utils.config_build(config, release_mode, target)
            self.config["target"] = target
            # print(self.config)

    def load_files(self):
        gumpath = gum_utils.get_gumpath()
        dirmaps = {}
        _, files = gum_utils.list_dir(os.path.join(gumpath, "dirmaps"))
        for path in files:
            _, name = os.path.split(path)
            with open(path) as temp:
                dirmaps[name] = json.load(temp)
        self.dirmaps = dirmaps

if __name__ == "__main__":
    g = Gum()