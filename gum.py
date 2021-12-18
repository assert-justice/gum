import os,sys, subprocess, json, datetime
import toml
import gum_parse, gum_utils, templates

__version__ = "0.0.1"

class Gum():
    def __init__(self):
        self.cwd = os.getcwd()
        # Load templates and default config.
        self.load_files()
        # Calls the parser.
        gum_parse.parse(self.create, self.build, self.run, self.install, self.acp, self.add, __version__)
        pass
    def create(self, args):
        print(args)
        temps = {
            "config": lambda: templates.config(args["name"], args["compiler"], args["language"], args["header"], args["src"]),
            "gitignore": templates.gitignore,
            "c_main": lambda: templates.c_main(args["name"], datetime.date.today()),
            "readme": lambda: templates.readme(args["name"])
        }
        dirmap = self.dirmaps["project.json"]
        path = os.path.join(self.cwd, args["name"])
        if os.path.exists(path):
            gum_utils.error(f"the project directory '{path}' already exists!")
        gum_utils.walk_dirmap(dirmap, path, True, temps)
        if args["vcs"] == "git":
            subprocess.run("git init".split(), cwd=os.path.join(self.cwd, args["name"]))
        pass
    def build(self, args):
        self.prime(args["release"], args["target"])
        config = self.config
        o_level = args.pop('o')
        if o_level:
            config["optimization"] = f"-O{o_level}"
        config["options"].append(config.pop("optimization"))
        for k,v in args.items():
            config[k] = v
        outname = config["name"]
        if gum_utils.get_os() == "win":
            outname += ".exe"
        dest = os.path.join(self.cwd, "bin", "release" if config["release"] else "debug", outname)
        config["dest"] = dest
        self.config = config
        files = gum_utils.grab_files(os.path.join(self.cwd, "src"), config["src"])
        command = []
        command.append(config["compiler"])
        command += config["options"]
        command += ["-o", dest] + files
        return subprocess.run(command).returncode == 0
    def run(self, args):
        if self.build(args):
            subprocess.run([self.config["dest"]])
    def install(self, args):
        pass
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
        name = args["name"]
        h_ext = self.config["header"]
        s_ext = self.config["src"]
        h_name = f"{name}{h_ext}"
        s_name = f"{name}{s_ext}"
        h = templates.c_head(name)
        s = templates.c_src(h_name)
        hp = os.path.join(self.cwd, "src", args["path"])
        sp = os.path.join(self.cwd, "src", args["path"])
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
    def prime(self, release_mode = False, target = "gnu"):
        # validate file structure
        # set config field
        dirmap = self.dirmaps["project.json"]
        gum_utils.walk_dirmap(dirmap, self.cwd)
        with open(os.path.join(self.cwd, "gum.toml")) as tom:
            config = toml.load(tom)
            self.config = gum_utils.config_build(config, release_mode, target)
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