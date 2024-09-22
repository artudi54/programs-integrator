import pkg_resources
import sortedcontainers
import numpy
from PySide6 import QtWidgets
from PySide6 import QtCore
from programs_integrator.user.SelfUiLoader import SelfUiLoader


class ConfigDialog(QtWidgets.QDialog):
    config_changed = QtCore.Signal()
    update_requested = QtCore.Signal()

    def __init__(self, configuration):
        super().__init__()
        ui_file_path = pkg_resources.resource_filename(__name__, "ConfigDialog.ui")
        SelfUiLoader(self).load(str(ui_file_path))

        self.configuration = configuration

        self._original_excluded_text = "\n".join(self.configuration.excluded_desktop_entries)
        self._original_title = self.windowTitle()
        self._unsaved_title = '*' + self._original_title

        self._fill_widgets()
        self._connect_signals()

    def _connect_signals(self):
        self.ok_button.clicked.connect(self._accept_dialog)
        self.apply_button.clicked.connect(self._apply_config)
        self.cancel_button.clicked.connect(self.close)
        self.update_button.clicked.connect(self.update_requested)

        self.update_delay_input.textChanged.connect(self._update_window_name)
        self.append_extension_button.toggled.connect(self._update_window_name)
        self.use_original_filename_button.toggled.connect(self._update_window_name)
        self.excluded_desktop_entries_input.textChanged.connect(self._update_window_name)

    def _fill_widgets(self):
        self.update_delay_input.setText(str(self.configuration.update_delay))
        self.append_extension_button.setChecked(self.configuration.append_extension)
        self.use_original_filename_button.setChecked(self.configuration.use_original_filename)
        self.excluded_desktop_entries_input.setPlainText("\n".join(self.configuration.excluded_desktop_entries))

        for i in range(len(self.configuration.application_dirs)):
            name_item = QtWidgets.QTableWidgetItem(self.configuration.application_dirs[i].name)
            path_item = QtWidgets.QTableWidgetItem(str(self.configuration.application_dirs[i].path))
            self.application_directories_table.insertRow(i)
            self.application_directories_table.setItem(i, 0, name_item)
            self.application_directories_table.setItem(i, 1, path_item)

    @QtCore.Slot()
    def _update_window_name(self):
        if (self.update_delay_input.text() != str(self.configuration.update_delay) or
            self.append_extension_button.isChecked() != self.configuration.append_extension or
            self.use_original_filename_button.isChecked() != self.configuration.use_original_filename or
            self.excluded_desktop_entries_input.toPlainText() != self._original_excluded_text):
            self.setWindowTitle(self._unsaved_title)
        else:
            self.setWindowTitle(self._original_title)

    @QtCore.Slot()
    def _apply_config(self):
        try:
            update_delay = int(self.update_delay_input.text())
            if update_delay <= 0 or (update_delay * 1000) > numpy.iinfo(numpy.int32).max:
                raise ValueError()
            self.configuration.update_delay = update_delay
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Invalid input", "Entered update delay is invalid or too big")
            return False
        self.configuration.append_extension = self.append_extension_button.isChecked()
        self.configuration.use_original_filename = self.use_original_filename_button.isChecked()

        self.configuration.excluded_desktop_entries =\
            sortedcontainers.SortedSet(filter(None, self.excluded_desktop_entries_input.toPlainText().splitlines()))
        self.config_changed.emit()
        self.setWindowTitle(self._original_title)
        return True

    @QtCore.Slot()
    def _accept_dialog(self):
        if self._apply_config():
            self.accept()

