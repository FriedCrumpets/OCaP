#! python3

import sys
from PySide2.QtWidgets import QWidget, QApplication, QGraphicsWidget
from PySide2.QtWidgets import *
from PySide2.QtGui import QIcon, QPainter, QColor, QMouseEvent
from PySide2.QtCore import QPoint, Qt


class newSheet(QWidget):
    def __init__(self, parent=None):
        super(newSheet, self).__init__(parent)

        self.setVisible(True)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowIcon(QIcon('ekm-logo-glyph-blue.png'))
        self.setFixedSize(124, 124)

        self.location = ''
        self.islocationSelected = False

    def __call__(self):
        pass

    def paintEvent(self, event):
        qp = QPainter(self)
        if not self.islocationSelected:
            qp.setPen(QColor(175, 191, 191))
            qp.setBrush(QColor(175, 191, 191))#247,247,235
        else:
            qp.setBrush(QColor(50, 168, 82))
        download = qp.drawEllipse(QPoint(62,62), 62, 62)
#
#   Event handling methods
#
    def mousePressEvent(self, event):
        if QMouseEvent.button(event) == Qt.LeftButton:
            self.loadLocation()

        if QMouseEvent.button(event) == Qt.RightButton:
            self.loadLocation()

        if QMouseEvent.button(event) == Qt.MiddleButton:
            pass

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

    def mouseDoubleClickEvent(self, event):
        pass

    def closeEvent(self, event):
        pass

#
#   Sub Methods
#
    def ifLoaded(self, location):
        return True if location else False

    def loadLocation(self):
        location = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.islocationSelected = self.ifLoaded(location)
        if self.islocationSelected:
            self.location = location

    def getLocation(self):
        if self.islocationSelected:
            self.update()
            return self.location

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    main = newSheet()
    main.show()
    sys.exit(app.exec_())
