import os, subprocess, json, datetime
import toml
import gum_parse, gum_utils, gum_config, gum_templates

__version__ = gum_config.version

class Gum():
    def __init__(self):
        self.cwd = os.getcwd()
        # Load templates and default config.
        self.load_files()
        # Calls the parser.
        gum_parse.parse(self.create, self.build, self.run, self.install, self.acp, self.add)

    def create(self, args):
        print(args)
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
        config = self.config
        o_level = args.pop('o')
        if o_level:
            config["optimization"] = f"-O{o_level}"
        config["options"].append(config.pop("optimization"))
        # for k,v in args.items():
        #     config[k] = v
        config["release"] = args["release"]
        outname = config["name"]
        os_ = "gnu"
        if gum_utils.get_os() == "win":
            outname += ".exe"
        dest = os.path.join(self.cwd, "bin", "release" if config["release"] else "debug", outname)
        config["dest"] = dest
        self.config = config
        files = gum_utils.grab_files(os.path.join(self.cwd, "src"), config["src"])
        command = []
        command.append(config["compiler"])
        command += config["options"]
        command.append("-Iinclude")
        command += ["-o", dest] + files
        command.append("-Llibs")
        command += gum_utils.grab_files(os.path.join(self.cwd, "libs"), gum_config.os_lib_extension[config["target"]])
        if "libs" in config:
            command += config["libs"]
        return subprocess.run(command).returncode == 0
    
    def compile_libs(self, names = None):
        libs_path = os.path.join(self.cwd, "deps")
        lib_extension = gum_config.os_lib_extension[self.config["target"]]
        if not names:
            names, _ = gum_utils.list_dir(libs_path)
        for name in names[:]:
            l_path = os.path.join(libs_path, name)
            gum_utils.walk_dirmap(self.dirmaps["lib.json"], l_path)
        for name in names[:]:
            l_path = os.path.join(libs_path, name)
            files = gum_utils.grab_files(l_path, lib_extension)
            for file in files:
                _, fname = os.path.split()

    def run(self, args):
        if self.build(args):
            subprocess.run([self.config["dest"]])

    def install(self, args):
        print(args)
        if args["name"]:
            path = os.path.join(self.cwd, "deps", args["name"])
            if os.path.exists(path):
                gum_utils.error(f"Cannot create library at '{path}', directory already exists.")
            gum_utils.walk_dirmap(self.dirmaps["lib.json"], path, True)
            if not args["manual"]:
                path = os.path.join(self.cwd, "include", args["name"])
                gum_utils.write_prep(path)
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
        print(args)
        name = args["name"]
        h_ext = self.config["header"]
        s_ext = self.config["src"]
        h_name = f"{name}{h_ext}"
        s_name = f"{name}{s_ext}"
        h = gum_templates.c_head(name)
        s = gum_templates.c_src(h_name)
        if not args["lib"]:
            hp = os.path.join(self.cwd, "src", args["path"])
            sp = os.path.join(self.cwd, "src", args["path"])
        else:
            libname = args["lib"]
            dirmap = self.dirmaps["lib.json"]
            gum_utils.walk_dirmap(dirmap, os.path.join(self.cwd, "deps", libname))
            hp = os.path.join(self.cwd, "deps", libname, "include", args["path"])
            sp = os.path.join(self.cwd, "deps", libname, "src", args["path"])
        if gum_utils.write_prep(hp, h_name) and gum_utils.write_prep(sp, s_name):
            pass
        else:
            return
        hp = os.path.join(hp, h_name)
        sp = os.path.join(sp, s_name)
        with open(hp, "w") as h_new:
            with open(sp, "w") as s_new:
                h_new.write(h)
                s_new.write(s)

    def prime(self, release_mode = False, target = None):
        # validate file structure
        # set config field
        if not target:
            target = gum_utils.get_os()
            #print("target", target)
        dirmap = self.dirmaps["validate.json"]
        gum_utils.walk_dirmap(dirmap, self.cwd)
        with open(os.path.join(self.cwd, "gum.toml")) as tom:
            config = toml.load(tom)
            self.config = gum_utils.config_build(config, release_mode, target)
            self.config["target"] = target
            print(self.config)

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