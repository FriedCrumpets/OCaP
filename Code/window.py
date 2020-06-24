import os, time, threading, webbrowser, Errors, traceback
from PySide2.QtWidgets import QMainWindow, QWidget, QMessageBox, QProgressBar, QProgressDialog, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QGraphicsWidget
from PySide2.QtGui import QIcon, QMouseEvent
from PySide2.QtCore import QSize, Qt
from old import oldSheet
from new import newSheet
from submit import Execute

class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.show()

        self.setWindowTitle('EKM Converter')
        self.setWindowIcon(QIcon('logo.png'))
        self.setFixedSize(QSize(184, 434))
        # self.resizable(False)

        self.input, self.output, self.button = self.load()
        self.output.update()
        self.output.show()
        self.button.clicked.connect(self.clicked)

    def mousePressEvent(self, event):
        if QMouseEvent.button(event) == Qt.LeftButton:
            pass

        if QMouseEvent.button(event) == Qt.RightButton:
            pass

    def reset(self):
        self.reset_loaded_files()
        self.reset_loaded_location()

    def reset_loaded_files(self):
        self.input.files = ''
        self.input.dataLoaded = False
        self.input.update()

    def reset_loaded_location(self):
        self.output.location = ''
        self.output.islocationSelected = False
        self.output.update()

    def clicked(self):
        if self.input.dataLoaded and self.output.islocationSelected:
            # TODO: Launches loading widget and disables gui until process has finished
            self.convert = Execute(self)

            msgBox = QMessageBox()
            msgBox.setWindowTitle('Converter')

            try:
                for x in self.convert(): # Conversion starts here
                    continue

                msgBox.setText('Converted')
                msgBox.exec_()
            except Errors.IncorrectFile:
                msgBox.setText('''File not Recognised''')
                msgBox.exec_()
            except PermissionError:
                msgBox.setText(''' Please Close down the Spreadsheet before attempting to convert it''')
                msgBox.exec_()
            except UnicodeDecodeError:
                msgBox.setText(''' File Encoding isn't compatible
                Encoding must be in unicode
                Click on 'Help' for a guide on how to change encoding using Excel
                ''')
                help = msgBox.addButton('Help', QMessageBox.HelpRole)
                msgBox.exec_()
                if msgBox.clickedButton() == help:
                    webbrowser.open('https://support.office.com/en-us/article/choose-text-encoding-when-you-open-and-save-files-60d59c21-88b5-4006-831c-d536d42fd861', 2)
            except Exception as e:
                s = ''
                msgBox.setText('''Unknown Error has Occured:

                ''' + repr(e) + " : \n")
                traceback.print_exc()
                msgBox.exec_()
            finally:
                self.reset()
        else:
            msg = QMessageBox()
            msg.setWindowTitle('Converter')
            msg.setText('Select Files for Conversion')
            msg.exec_()

    def forceUpdate(self):
        self.input.update()
        self.output.update()

    def load(self):
        Hlayout, Vlayout = self.loadLayouts()
        input, output, button = self.loadWidgets()
        Vlayout.addWidget(input)
        Vlayout.addWidget(button)
        Vlayout.addWidget(output)
        Hlayout.addLayout(Vlayout)
        self.setLayout(Hlayout)
        return input, output, button

    def loadWidgets(self):
        input = oldSheet()
        output = newSheet()
        button = QPushButton('Convert')
        return input, output, button

    def loadLayouts(self):
        Hlayout = QHBoxLayout()
        Vlayout = QVBoxLayout()
        return Hlayout, Vlayout

import sys
app = QApplication(sys.argv)
test = Window()
sys.exit(app.exec_())
