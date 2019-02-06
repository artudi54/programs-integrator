import os
import sys
from programs_integrator.desktoputils.DesktopEntry import DesktopEntry


class StructureMaker:
    class Programs:
        def __init__(self, configuration):
            self.path = configuration.user.home_path / "Programs"
            self.autostart_path = self.path / "Autostart"
            self.application_dirs_path = self.path / "ApplicationDirs"

    def __init__(self, configuration):
        self.configuration = configuration
        self.programs = StructureMaker.Programs(self.configuration)

        self.create_directories()

    def create_directories(self):
        if not self.programs.path.exists():
            try:
                self.programs.path.mkdir(exist_ok=True)
            except OSError as exc:
                print("Warning: " + str(exc), file=sys.stderr)

        if not self.programs.autostart_path.exists():
            try:
                os.symlink(self.configuration.user.autostart_path, self.programs.autostart_path)
            except OSError as exc:
                print("Warning: " + str(exc), file=sys.stderr)

        elif self.programs.autostart_path.resolve() != self.configuration.user.autostart_path:
            try:
                os.remove(self.programs.autostart_path)
                os.symlink(self.configuration.user.autostart_path, self.programs.autostart_path)
            except OSError as exc:
                print("Warning: " + str(exc), file=sys.stderr)

        if not self.programs.application_dirs_path.exists():
            try:
                self.programs.application_dirs_path.mkdir(exist_ok=True)
            except OSError as exc:
                print("Warning: " + str(exc), file=sys.stderr)

    def update(self):
        self.create_directories()
        self.configuration.update_application_dirs()
        self.update_application_dirs()
        self.update_desktop_entries()

    def update_application_dirs(self):
        entries_dict = StructureMaker._directory_symlinks_dict(self.programs.application_dirs_path)
        if entries_dict is None:
            print("Error: updating application directories failed")
            return

        for application_dir in self.configuration.application_dirs:
            if application_dir.name in entries_dict:
                symlink_path = entries_dict[application_dir.name]
                if symlink_path != application_dir.path:
                    try:
                        os.remove(self.programs.application_dirs_path / application_dir.name)
                        os.symlink(application_dir.path, self.programs.application_dirs_path / application_dir.name)
                    except OSError as exc:
                        print("Waring: " + str(exc), file=sys.stderr)
                entries_dict.pop(application_dir.name)
            else:
                try:
                    os.symlink(application_dir.path, self.programs.application_dirs_path / application_dir.name)
                except OSError as exc:
                    print("Waring: " + str(exc), file=sys.stderr)
        for entry in entries_dict:
            try:
                os.remove(self.programs.application_dirs_path / entry)
            except OSError as exc:
                print("Waring: " + str(exc), file=sys.stderr)

    def update_desktop_entries(self):
        entries_dict = StructureMaker._directory_symlinks_dict(self.programs.path)
        if entries_dict is None:
            print("Error: updating desktop entries failed", file=sys.stderr)
            return

        desktop_entries = self._list_desktop_entries()

        for desktop_entry in desktop_entries:
            if desktop_entry.filename in self.configuration.excluded_desktop_entries:
                continue
            filename = desktop_entry.make_filename(self.configuration.append_extension,
                                                   self.configuration.use_original_filename)
            if filename in entries_dict:
                symlink_path = entries_dict[filename]
                if symlink_path != desktop_entry.path:
                    try:
                        os.remove(self.programs.path / filename)
                        os.symlink(desktop_entry.path, self.programs.path / filename)
                    except OSError as exc:
                        print("Warning: " + str(exc), file=sys.stderr)
                entries_dict.pop(filename)
            else:
                try:
                    os.symlink(desktop_entry.path, self.programs.path / filename)
                except OSError as exc:
                    print("Warning: " + str(exc), file=sys.stderr)

        for (entry, path) in entries_dict.items():
            if not path.is_dir():
                try:
                    os.remove(self.programs.path / entry)
                except OSError as exc:
                    print("Warning: " + str(exc), file=sys.stderr)

    @staticmethod
    def _directory_symlinks_dict(directory):
        try:
            entries = os.listdir(directory)
            entries = [entry for entry in entries if (directory / entry).is_symlink()]
            return dict((entry, (directory / entry).resolve()) for entry in entries)
        except OSError as exc:
            print("Warning: " + str(exc), file=sys.stderr)
            return None

    def _list_desktop_entries(self):
        desktop_entries = []
        for application_dir in self.configuration.application_dirs:
            try:
                files = os.listdir(application_dir.path)
            except OSError as exc:
                print("Waring: " + str(exc), file=sys.stderr)
                continue
            for file in files:
                file_path = application_dir.path / file
                if file_path in self.configuration.excluded_desktop_entries:
                    continue
                desktop_entry = DesktopEntry(application_dir.path / file)
                if desktop_entry.is_valid():
                    desktop_entries.append(desktop_entry)
        return desktop_entries
