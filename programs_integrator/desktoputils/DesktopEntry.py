from pathlib import Path
import configparser


class DesktopEntry:
    def __init__(self, path: Path) -> None:
        self.path: Path = path
        self.filename = str(self.path.name)
        self.name: str | None = None
        self.display: bool = True
        self.__read_properties()

    def is_valid(self):
        return self.name is not None and self.display

    def make_filename(self, append_extension=True, use_original_filename=True) -> str | None:
        if not self.is_valid():
            return None
        name = self.name
        if use_original_filename:
            name = str(self.path.stem)
        if append_extension:
            name += str(self.path.suffix)
        return name

    def __read_properties(self) -> None:
        section_desktop_entry = "Desktop Entry"
        key_name = "Name"
        key_no_display = "NoDisplay"

        try:
            parser = configparser.ConfigParser()
            parser.read(self.path)
            if section_desktop_entry in parser:
                desktop_entry = parser[section_desktop_entry]
                if key_name in desktop_entry:
                    self.name = desktop_entry[key_name]
                if key_no_display in desktop_entry:
                    no_display_raw = desktop_entry.getboolean(key_no_display)
                    self.display = not no_display_raw
        except (configparser.Error, OSError) as exc:
            print(f"Warning: {exc}")
            pass
