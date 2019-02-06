from programs_integrator.config.ApplicationDir import ApplicationDir
import pathlib


class UserApplicationDir(ApplicationDir):
    def __init__(self, home_path: pathlib.Path):
        super().__init__()
        self.name = "UserApplications"
        self.path = home_path / ".local" / "share" / "applications"
