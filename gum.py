import sys, os, shutil, toml, subprocess

__version__ = "0.0.0"

class Gum():
    def __init__(self) -> None:
        self.cwd = os.getcwd()
        args = sys.argv
        self.args = args
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
            "gum.toml":""
        }
        self.templates = {
            "gum.toml": self.format_config,
        }
        command = args[1]
        if command == "create":
            # create new project
            self.create()
            return
        # validate project structure
        # grab config toml
        commands = {
            "build": self.build,
            "run": self.run,
            "script": self.script
        }
        if not command in commands:
            # error, unrecognized command
            self.error(f"unrecognized command '{command}'")
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
    def create_dirmap(self, path = None):
        pass
    def create(self):
        if len(self.args) < 3:
            self.error("not enough arguments provided to 'create', requires a project name")
        self.name = self.args[2]
        self.validate_name(self.name)
        # create config toml
        # create directories & file templates
        pass
    def format_config(self):
        pass
    def build(self):
        pass
    def run(self):
        pass
    def script(self):
        pass

if __name__ == "__main__":
    gum = Gum()