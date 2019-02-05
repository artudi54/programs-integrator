import pathlib
import os
from programs_integrator.desktoputils.DesktopEntry import DesktopEntry


class StructureMaker:
    PROGRAMS = "Programs"
    AUTOSTART = "Autostart"
    APPLICATIONS_DIRS = "ApplicationDirs"

    def __init__(self, configuration):
        self.configuration = configuration
        self.programs_path = pathlib.Path(self.configuration.user.home_path) / StructureMaker.PROGRAMS
        self.programs_autostart_path = self.programs_path / StructureMaker.AUTOSTART
        self.programs_application_dirs_path = self.programs_path / StructureMaker.APPLICATIONS_DIRS

        self.create_directories()

    def create_directories(self):
        if not self.programs_path.exists():
            self.programs_path.mkdir(exist_ok=True)
        if not self.programs_autostart_path.exists():
            os.symlink(str(self.configuration.user.autostart_path), self.programs_autostart_path)
        if not self.programs_application_dirs_path.exists():
            self.programs_application_dirs_path.mkdir(exist_ok=True)

    def update(self):
        self.create_directories()
        self.configuration.update_application_dirs()
        self.update_application_dirs()
        self.update_desktop_entries()

    def update_application_dirs(self):
        entries_dict = StructureMaker.directory_symlinks_dict(self.programs_application_dirs_path)
        for application_dir in self.configuration.application_dirs:
            if application_dir.name in entries_dict:
                symlink_path = entries_dict[application_dir.name]
                if symlink_path != application_dir.path:
                    os.remove(self.programs_application_dirs_path / application_dir.name)
                    os.symlink(application_dir.path, self.programs_application_dirs_path / application_dir.name)
                entries_dict.pop(application_dir.name)
            else:
                os.symlink(application_dir.path, self.programs_application_dirs_path / application_dir.name)
        for entry in entries_dict:
            os.remove(self.programs_application_dirs_path / entry)

    def update_desktop_entries(self):
        entries_dict = StructureMaker.directory_symlinks_dict(self.programs_path)

        desktop_entries = []
        for application_dir in self.configuration.application_dirs:
            files = os.listdir(application_dir.path)
            for file in files:
                file_path = application_dir.path / file
                if file_path in self.configuration.excluded_desktop_entries:
                    continue
                desktop_entry = DesktopEntry(application_dir.path / file)
                if desktop_entry.is_valid():
                    desktop_entries.append(desktop_entry)

        for desktop_entry in desktop_entries:
            if desktop_entry.filename in self.configuration.excluded_desktop_entries:
                continue
            if desktop_entry.name in entries_dict:
                symlink_path = entries_dict[desktop_entry.name]
                if symlink_path != desktop_entry.path:
                    os.remove(self.programs_path / desktop_entry.name)
                    os.symlink(desktop_entry.path, self.programs_path / desktop_entry.name)
                entries_dict.pop(desktop_entry.name)
            else:
                try:
                    os.symlink(desktop_entry.path, self.programs_path / desktop_entry.name)
                except Exception as exc:
                    print(exc)

        for (entry, path) in entries_dict.items():
            if not path.is_dir():
                os.remove(self.programs_path / entry)

    @staticmethod
    def directory_symlinks_dict(directory):
        entries = os.listdir(directory)
        entries = [entry for entry in entries if (directory / entry).is_symlink()]
        return dict((entry, (directory / entry).resolve()) for entry in entries)
