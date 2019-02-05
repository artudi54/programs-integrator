import pathlib


class ApplicationDir:
    _MAPPING = {
        "/usr/share": "SystemApplications",
        "/usr/local/share": "LocalSystemApplications",
        "/var/lib/snapd/desktop": "SnapApplications"
    }

    def __init__(self, path: pathlib.Path = None):
        if path is None:
            self.name = None
            self.path = None
            return
        path = str(path)
        if path.endswith("/"):
            path = path[:-1]

        self.name = ApplicationDir._make_name(path)
        self.path = ApplicationDir._make_path(path)

    def exists(self):
        return self.path is not None and self.path.exists()

    @staticmethod
    def _make_name(path):
        if path in ApplicationDir._MAPPING:
            return ApplicationDir._MAPPING[path]
        parts = pathlib.Path(path).parts
        name = parts[-1]
        if parts[-1] == 'share':
            name = parts[-2]
        name = name[0].upper() + name[1:]
        return name + "Applications"

    @staticmethod
    def _make_path(path):
        return pathlib.Path(path) / "applications"
