import sys
import signal
import pathlib
import pkg_resources
import dbus
import dbus.bus
import dbus.service
import dbus.mainloop.glib
from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6 import QtGui
from programs_integrator.desktoputils import StructureMaker
from programs_integrator.config import Config
from programs_integrator import user


DBUS_NAME = "com.ProgramsIntegrator"
DBUS_OBJECT_NAME = "/ProgramsIntegrator"


class ProgramsIntegratorWorker(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.configuration = Config()
        self.structure_maker = StructureMaker(self.configuration)
        self.timer = QtCore.QTimer(self)
        self.config_dialog = None

        self.timer.timeout.connect(self.structure_maker.update)
        self.timer.setInterval(1000 * self.configuration.update_delay)
        self.configuration.write_config()

    def start(self):
        self.configuration.print()
        self.structure_maker.update()
        self.timer.start()

    def show_window(self):
        if self.config_dialog is not None:
            self.config_dialog.raise_()
            self.config_dialog.activateWindow()
            return

        self.config_dialog = user.ConfigDialog(self.configuration)
        self.config_dialog.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)

        self.config_dialog.destroyed.connect(self._handle_dialog_closed)
        self.config_dialog.update_requested.connect(self.structure_maker.update)
        self.config_dialog.config_changed.connect(self._handle_config_changed)

        self.config_dialog.show()
        self.config_dialog.raise_()
        self.config_dialog.activateWindow()

    @QtCore.Slot()
    def _handle_dialog_closed(self):
        self.config_dialog = None

    @QtCore.Slot()
    def _handle_config_changed(self):
        self.timer.setInterval(1000 * self.configuration.update_delay)
        self.configuration.write_config()


class ProgramsIntegrator(dbus.service.Object):
    def __init__(self, session_bus):
        dbus.service.Object.__init__(self, session_bus, DBUS_OBJECT_NAME)
        self.worker = ProgramsIntegratorWorker()

    @dbus.service.method(DBUS_NAME, in_signature='', out_signature='')
    def show_window(self):
        self.worker.show_window()

    def start(self):
        self.worker.start()


def handle_exception(exc):
    print(str(pathlib.Path(sys.argv[0]).name) + ": " + str(exc), file=sys.stderr)
    return 1


def run():
    try:
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        application = QtWidgets.QApplication(sys.argv)
        application.setQuitOnLastWindowClosed(False)
        icon_path = pkg_resources.resource_filename(__name__, "ProgramsIntegrator.png")
        application.setWindowIcon(QtGui.QIcon(icon_path))

        dbus_loop = dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        session_bus = dbus.SessionBus()
        if session_bus.request_name(DBUS_NAME) != dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER:
            raise RuntimeError("application already running")

        programs_integrator = ProgramsIntegrator(session_bus)
        programs_integrator.start()

        return application.exec_()
    except Exception as exc:
        return handle_exception(exc)


def notify():
    try:
        session_bus = dbus.SessionBus()
        if session_bus.request_name(DBUS_NAME) == dbus.bus.REQUEST_NAME_REPLY_PRIMARY_OWNER:
            raise RuntimeError("programs-integrator is not running")

        remote_object = session_bus.get_object(DBUS_NAME, DBUS_OBJECT_NAME)
        programs_integrator = dbus.Interface(remote_object, DBUS_NAME)
        programs_integrator.show_window()
    except Exception as exc:
        return handle_exception(exc)
