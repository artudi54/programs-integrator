#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="programs-integrator",
    version="0.1.dev0",
    author = "artudi54",
    description="Daemon program for dynamically generating 'Programs' directory",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/artudi54/programs-integrator",
    packages=find_packages(),
    package_data={"": ["*.ui"]},
    scripts=["bin/programs-integrator", "bin/programs-integrator-ctl"],
    data_files=[("share/icons", ["resources/share/icons/programs-integrator.svg"]),
                ("share/applications", ["resources/share/applications/programs-integrator.desktop"]),
                ("share/systemd/user", ["resources/share/systemd/user/programs-integrator.service"])],
    install_requires=open('requirements.txt').read().splitlines()
)
