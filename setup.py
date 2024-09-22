#!/usr/bin/env python3
from setuptools import setup, find_packages
from distutils.command.install import install
from distutils.errors import DistutilsSetupError
from pathlib import Path
from shutil import copy2
from os import system


class SystemdInstall(install):
    def install_systemd(self):
        service_name = "programs-integrator.service"
        print("Registering systemd service")
        if (system("systemctl --user daemon-reload") != 0 or
            system("systemctl --user enable " + service_name) != 0 or
            system("systemctl --user start " + service_name) != 0):
            raise DistutilsSetupError("Registering systemd service failed")

    def run(self):
        install.run(self)
        print("running install_systemd")
        self.install_systemd()


setup(
    name="programs-integrator",
    version="0.1.dev",
    author="artudi54",
    description="Daemon program for dynamically generating 'Programs' directory",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={"": ["*.ui"]},
    scripts=["bin/programs-integrator", "bin/programs-integrator-ctl"],
    data_files=[("share/icons", ["resources/share/icons/programs-integrator.svg"]),
                ("share/applications", ["resources/share/applications/programs-integrator.desktop"]),
                ("share/systemd/user", ["resources/share/systemd/user/programs-integrator.service"])],
    cmdclass={'install': SystemdInstall},
    install_requires=open('requirements.txt').read().splitlines()
)
