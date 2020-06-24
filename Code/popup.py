from PySide2.QtWidgets import QInputDialog, QLineEdit
from PySide2.QtCore import QDir

class popup(QInputDialog):
    def __init__(self, filename, parent=None):
        super(popup, self).__init__(parent)
        self.filename = filename

    def __call__(self):
        super(popup,self).__call__(parent)

    def popup(self):
        text, ok = self.getText(None, self.filename,
                                         "Location of customer Images", QLineEdit.Normal,
                                         '')
        return text
