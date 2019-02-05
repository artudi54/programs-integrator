import pathlib
import configparser


class DesktopEntry:
    def __init__(self, path):
        self.path = pathlib.Path(path)
        self.filename = self.path.name
        self.name = DesktopEntry._read_name(self.path)

    def is_valid(self):
        return self.name is not None

    @staticmethod
    def _read_name(path):
        section_desktop_entry = "Desktop Entry"
        key_name = "Name"

        try:
            parser = configparser.ConfigParser()
            parser.read(path)
            if section_desktop_entry in parser:
                desktop_entry = parser[section_desktop_entry]
                if key_name in desktop_entry:
                    return desktop_entry[key_name]
            return None
        except (configparser.Error, OSError):
            return None
