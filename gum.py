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
            "c_main": lambda: templates.c_main(args["name"], datetime.date.today())
        }
        dirmap = self.dirmaps["project.json"]
        path = os.path.join(self.cwd, args["name"])
        if os.path.exists(path):
            gum_utils.error(f"the project directory '{path}' already exists!")
        gum_utils.walk_dirmap(temps, dirmap, path, True)
        if args["vcs"] == "git":
            subprocess.run("git init".split(), cwd=os.path.join(self.cwd, args["name"]))
        pass
    def build(self, args):
        pass
    def run(self, args):
        pass
    def install(self, args):
        pass
    def acp(self, args):
        pass
    def add(self, args):
        pass
    def safe_write(self, path, contents):
        # Given a path create directories as needed. When in correct directory checks if file already exists. 
        # If so it asks for comfirmation before overwriting.
        pass
    def prime(self):
        # validate file structure
        # set config field
        pass
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