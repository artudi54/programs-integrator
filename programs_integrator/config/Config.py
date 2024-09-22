import os
import sys
import pathlib
import configparser
import sortedcontainers
from programs_integrator.config.ApplicationDir import ApplicationDir
from programs_integrator.config.UserApplicationDir import UserApplicationDir


class Config:
    SECTION_CONFIG = "Config"
    KEY_APPEND_EXTENSION = "AppendExtension"

    def __init__(self):
        self.home_path = pathlib.Path.home()
        self.autostart_path = self.home_path / ".config" / "autostart"
        self.config_dir = self.home_path / ".config" / "desktop-entry-integrator"
        self.config_file = self.config_dir / "config.ini"
        self.excluded_file = self.config_dir / "excluded.txt"

        self.application_dirs = Config._read_application_dirs(self.home_path)

        self.append_extension = True
        self.update_delay = 10
        self.excluded_desktop_entries = set()

        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_file.exists():
            self.config_file.touch(exist_ok=True)
        if not self.excluded_file.exists():
            self.excluded_file.touch(exist_ok=True)
        self.read_config()

    @staticmethod
    def _read_application_dirs(home_path):
        application_dirs = []

        xdg_dirs_str = os.environ["XDG_DATA_DIRS"]
        xdg_dirs = xdg_dirs_str.split(":")

        for xdg_dir in xdg_dirs:
            application_dir = ApplicationDir(xdg_dir)
            if application_dir.exists():
                application_dirs.append(application_dir)

        user_application_dir = UserApplicationDir(home_path)
        if user_application_dir.exists():
            application_dirs.append(user_application_dir)

        return application_dirs

    def read_config(self):
        parser = configparser.ConfigParser()
        parser.read(self.config_dir)

        if Config.SECTION_CONFIG in parser:
            config_section = parser[Config.SECTION_CONFIG]
            if Config.KEY_APPEND_EXTENSION in config_section:
                self.append_extension = config_section[Config.KEY_APPEND_EXTENSION]

        self.excluded_desktop_entries = sortedcontainers.SortedSet(filter(None, open(self.excluded_file).read().splitlines()))

    def write_config(self):
        parser = configparser.ConfigParser()
        parser[Config.SECTION_CONFIG] = {
            Config.KEY_APPEND_EXTENSION: str(self.append_extension)
        }
        with open(self.config_file, "w") as configfile:
            parser.write(configfile)

    def update_application_dirs(self):

        self.application_dirs = Config._read_application_dirs(self.home_path)

    def print(self, file=sys.stdout):
        print("Config is:", file=file)
        print("\t" + Config.KEY_APPEND_EXTENSION + "=" + str(self.append_extension), file=file)
        print("\tApplicationDirs:")
        for application_dir in self.application_dirs:
            print("\t\t" + application_dir.name + ":", str(application_dir.path), file=file)
        print(file=file)
