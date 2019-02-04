from programs_integrator.config.ApplicationDir import ApplicationDir
import pathlib


class UserApplicationDir(ApplicationDir):
    def __init__(self, home_path):
        ApplicationDir.__init__(self)
        self.name = "UserApplications"
        self.path = pathlib.Path(home_path) / ".local" / "share" / "applications"
