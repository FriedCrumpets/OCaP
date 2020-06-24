#! python3
import sys
from PySide2.QtWidgets import QWidget, QApplication, QGraphicsWidget
from PySide2.QtGui import QIcon, QPainter, QColor, QMouseEvent
from PySide2.QtWidgets import *
from PySide2.QtCore import QPoint, Qt

class oldSheet(QWidget):
    def __init__(self, parent=None):
        super(oldSheet, self).__init__(parent)

        self.setVisible(True)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowIcon(QIcon('ekm-logo-glyph-blue.png'))
        self.setFixedSize(124, 124)

        self.setAcceptDrops(True)
        self.droppable = False

        self.files = ''
        self.dataLoaded = False

    def __call__(self):
        pass

    def paintEvent(self, event):
        qp = QPainter(self)
        if not self.dataLoaded:
            qp.setPen(QColor(175, 191, 191))
            qp.setBrush(QColor(175, 191, 191))#247,247,235
        else:
            qp.setBrush(QColor(50, 168, 82))
        upload = qp.drawEllipse(QPoint(62,62), 62, 62)
        # downloadBox = qp.drawEllipse(QPoint(372,124), 64, 64)
#
#   Event handling methods
#

    def mousePressEvent(self, event):
        if QMouseEvent.button(event) == Qt.LeftButton:
            self.fileExplore()

        if QMouseEvent.button(event) == Qt.RightButton:
            self.fileExplore()
            # self.loadFiles(self.files)

        if QMouseEvent.button(event) == Qt.MiddleButton:
            pass

    def dragEnterEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            event.setAccepted(True)
            self.droppable = True
        else:
            event.setAccepted(False)
            self.droppable = False

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasUrls() and self.droppable:
            urls = [x.toString() for x in mimeData.urls()]
            files = self.parseUrls(urls)

            self.dataLoaded = self.ifLoaded(files)
            if self.dataLoaded:
                self.update()
                self.files = files

    def dragLeaveEvent(self, event):
        self.droppable = False

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
    def parseUrls(self, urls):
        parsedUrls = []
        for url in urls:
            if url.endswith('.csv'):
                parsedUrls.append(url[8:])
        return parsedUrls

    def getFiles(self):
        if self.dataLoaded:
            return self.files
        # return readFiles, headerFiles, origin_list, column_location

    def ifLoaded(self, files):
        return True if files else False

    def fileExplore(self):
        files = QFileDialog.getOpenFileNames(self, "Open CSV File","/home/", "CSV Files (*.csv)");
        self.dataLoaded = self.ifLoaded(files[0])
        if self.dataLoaded:
            self.files = files[0]

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    main = oldSheet()
    main.show()
    sys.exit(app.exec_())
