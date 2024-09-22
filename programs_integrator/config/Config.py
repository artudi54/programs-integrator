import os
import sys
import contextlib
import pathlib
import configparser
import distutils.util
import numpy
import sortedcontainers
from programs_integrator.config.ApplicationDir import ApplicationDir
from programs_integrator.config.UserApplicationDir import UserApplicationDir


class Config:
    _SECTION_CONFIG = "Config"
    _KEY_APPEND_EXTENSION = "AppendExtension"
    _KEY_USE_ORIGINAL_FILENAME = "UseOriginalFilename"
    _KEY_UPDATE_DELAY = "UpdateDelay"

    class User:
        def __init__(self):
            self.home_path = pathlib.Path.home()
            self.autostart_path = self.home_path / ".config" / "autostart"
            self.config_dir = self.home_path / ".config" / "programs-integrator"
            self.config_file = self.config_dir / "config.ini"
            self.excluded_file = self.config_dir / "excluded.txt"

    def __init__(self):
        self.user = Config.User()
        self.application_dirs = Config._read_application_dirs(self.user.home_path)

        self.append_extension = True
        self.use_original_filename = True
        self.update_delay = 10
        self.excluded_desktop_entries = set()

        if not self.user.config_dir.exists():
            self.user.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.user.config_file.exists():
            self.user.config_file.touch(exist_ok=True)
        if not self.user.excluded_file.exists():
            self.user.excluded_file.touch(exist_ok=True)
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
        parser.optionxform = str
        parser.read(self.user.config_file)

        if Config._SECTION_CONFIG in parser:
            config_section = parser[Config._SECTION_CONFIG]
            if Config._KEY_APPEND_EXTENSION in config_section:
                with contextlib.suppress(ValueError):
                    self.append_extension = bool(distutils.util.strtobool(config_section[Config._KEY_APPEND_EXTENSION]))
            if Config._KEY_USE_ORIGINAL_FILENAME in config_section:
                with contextlib.suppress(ValueError):
                    self.use_original_filename = bool(distutils.util.strtobool(config_section[Config._KEY_USE_ORIGINAL_FILENAME]))
            if Config._KEY_UPDATE_DELAY in config_section:
                with contextlib.suppress(ValueError):
                    update_delay = int(config_section[Config._KEY_UPDATE_DELAY])
                    if update_delay <= 0 or (update_delay * 1000) > numpy.iinfo(numpy.int32).max:
                        raise ValueError()
                    self.update_delay = update_delay

        self.excluded_desktop_entries =\
            sortedcontainers.SortedSet(filter(None, open(self.user.excluded_file).read().splitlines()))

    def write_config(self):
        parser = configparser.ConfigParser()
        parser.optionxform = str
        parser[Config._SECTION_CONFIG] = {
            Config._KEY_APPEND_EXTENSION: str(self.append_extension),
            Config._KEY_USE_ORIGINAL_FILENAME: str(self.use_original_filename),
            Config._KEY_UPDATE_DELAY: str(self.update_delay)
        }
        with self.user.config_file.open("w") as config_file:
            parser.write(config_file)
        with self.user.excluded_file.open("w") as excluded_file:
            for entry in self.excluded_desktop_entries:
                excluded_file.write(entry)
                excluded_file.write("\n")

    def update_application_dirs(self):
        self.application_dirs = Config._read_application_dirs(self.user.home_path)

    def print(self, file=sys.stdout):
        print("Config:", file=file)
        print("\t" + Config._KEY_APPEND_EXTENSION + "=" + str(self.append_extension), file=file)
        print("\t" + Config._KEY_USE_ORIGINAL_FILENAME + "=" + str(self.use_original_filename), file=file)
        print("\t" + Config._KEY_UPDATE_DELAY + "=" + str(self.update_delay), file=file)
        print("\tApplicationDirs:")
        for application_dir in self.application_dirs:
            print("\t\t" + application_dir.name + ":", str(application_dir.path), file=file)
        print("\tExcludedDesktopEntries:")
        for excluded_entry in self.excluded_desktop_entries:
            print("\t\t" + excluded_entry)
        print(file=file)
