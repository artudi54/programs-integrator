import pkg_resources
import sortedcontainers
from PySide2 import QtWidgets
from PySide2 import QtCore
from programs_integrator.user.SelfUiLoader import SelfUiLoader


class ConfigDialog(QtWidgets.QDialog):
    update_requested = QtCore.Signal()

    def __init__(self, configuration):
        super().__init__()
        ui_file_path = pkg_resources.resource_filename(__name__, "ConfigDialog.ui")
        SelfUiLoader(self).load(str(ui_file_path))

        self.configuration = configuration

        self._connect_signals()
        self._fill_widgets()

    def _connect_signals(self):
        self.cancel_button.clicked.connect(self.close)
        self.ok_button.clicked.connect(self._apply_config)
        self.update_button.clicked.connect(self.update_requested)

    def _fill_widgets(self):
        self.update_delay_input.setText(str(self.configuration.update_delay))
        self.append_extension.setChecked(self.configuration.append_extension)
        self.excluded_desktop_entries_input.setPlainText("\n".join(self.configuration.excluded_desktop_entries))

        for i in range(len(self.configuration.application_dirs)):
            name_item = QtWidgets.QTableWidgetItem(self.configuration.application_dirs[i].name)
            path_item = QtWidgets.QTableWidgetItem(str(self.configuration.application_dirs[i].path))
            self.application_directories_table.insertRow(i)
            self.application_directories_table.setItem(i, 0, name_item)
            self.application_directories_table.setItem(i, 1, path_item)

    def _apply_config(self):
        # TODO add check for input
        self.configuration.update_delay = int(self.update_delay_input.text())
        self.configuration.append_extension = self.append_extension.isChecked()

        self.configuration.excluded_desktop_entries =\
            sortedcontainers.SortedSet(filter(None, self.excluded_desktop_entries_input.toPlainText().splitlines()))

        self.accept()

