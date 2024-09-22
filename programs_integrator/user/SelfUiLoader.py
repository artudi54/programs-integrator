from PySide6 import QtUiTools


class SelfUiLoader(QtUiTools.QUiLoader):
    def __init__(self, widget):
        QtUiTools.QUiLoader.__init__(self, widget)
        self.widget = widget

    def createWidget(self, class_name, parent=None, name=''):
        if parent is None and self.widget:
            return self.widget
        else:
            widget = QtUiTools.QUiLoader.createWidget(self, class_name, parent, name)
            if self.widget:
                setattr(self.widget, name, widget)
            return widget
