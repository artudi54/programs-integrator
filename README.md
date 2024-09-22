# Programs Integrator
Programs integrator is a GNU/Linux daemon program, written in python, dynamicly generating "Programs" directory in user's home directory. It scans all XDG_DATA_DIRS periodically and makes symbolic links inside the managed directory to application desktop entries.

#### systemd
Program is running as user systemd service. User session with graphical environment is required to run and manage the program.

#### programs-integrator-ctl
It starts graphical tool managing configuration of the program. The configuration is stored in "~/.config/programs-integrator" directory. It let's you change settings, list destkop entries excluded from linking and provides you with information about XDG_DATA_DIRS.
![screenshot](https://raw.githubusercontent.com/artudi54/programs-integrator/master/Programs%20Integrator%20Configuration.png)

## Installation
Application supports only user install. System wide installation won't work, as this app serves as user-only service.

#### Installing package

##### Installing with PIP
programs-integrator is avalable as a PyPI package. It can be downloaded and installed with PIP
```bash
pip install --user programs-integrator
```

##### Manual installation
Installing program manually is not recommended, as application is not managed by any package manager. Manual installation can be done with "setup.py" script using setuputils package.
```bash
git clone https://github.com/artudi54/programs-integrator
cd programs-integrator
./setup.py install --single-version-externally-managed
```

#### Registering systemd service
To start the service it is required to enable systemd user service
```bash
systemctl --user daemon-reload
systemctl --user enable programs-integrator.service
systemctl --user start programs-integrator.service
```
