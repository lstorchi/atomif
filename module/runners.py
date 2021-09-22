from PyQt5.QtWidgets import (QDialog, QProgressBar, QPushButton, QGridLayout)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import QtGui, QtWidgets

import time

class runcudialog(QtWidgets.QDialog):

    def __init__(self, parent=None):

        super(runcudialog, self).__init__(parent)

        self.okbutton = QtWidgets.QPushButton('Start')
        self.okbutton.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        self.okbutton.clicked.connect(self.run)

        stepval_label = QtWidgets.QLabel("Step Value : ", self)
        self.stepval_line = QtWidgets.QLineEdit("1.0", self)
        self.stepval_line.move(20, 20)
        self.stepval_line.resize(280,40)

        deltaval_label = QtWidgets.QLabel("Delta Value : ", self)
        self.deltaval_line = QtWidgets.QLineEdit("5.0", self)
        self.deltaval_line.move(20, 20)
        self.deltaval_line.resize(280,40)

        self.ddielcheckbox = QtWidgets.QCheckBox("Enable Dielectric damping ", self)

        self.exportdxcheckbox = QtWidgets.QCheckBox("Export DX files ", self)

        self.grid = QtWidgets.QGridLayout(self)
        self.grid.addWidget(stepval_label, 0, 0)
        self.grid.addWidget(self.stepval_line, 0, 1)

        self.grid.addWidget(deltaval_label, 1, 0)
        self.grid.addWidget(self.deltaval_line, 1, 1)

        self.grid.addWidget(self.ddielcheckbox, 2, 0)
        self.grid.addWidget(self.exportdxcheckbox, 3, 0)

        self.grid.addWidget(self.okbutton, 4, 2)

    def run(self):

        self.close()

TIME_LIMIT = 100

class External(QThread):
    """
    Runs a counter thread.
    """
    countChanged = pyqtSignal(int)

    def run(self):
        count = 0
        while count < TIME_LIMIT:
            count +=1
            time.sleep(0.1)
            self.countChanged.emit(count)

            print(count)

class progressdia (QDialog):
    def __init__(self, parent=None):

        self.__cancelled__ = False
        super(progressdia, self).__init__(parent)
        
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Progress Bar')
        self.__progress__ = QProgressBar(self)
        self.__progress__.setGeometry(0, 0, 300, 25)
        self.__progress__.setMaximum(100)
        self.__button__ = QPushButton('Cancel', self)
        self.__button__.move(0, 30)
        self.__button__.clicked.connect(self.on_button_click)

        self.grid = QGridLayout(self)

        self.grid.addWidget(self.__progress__ , 0, 0)
        self.grid.addWidget(self.__button__, 1, 0)

    def set_label(self, label):
        self.setWindowTitle(label)

    def on_button_click(self):
        self.__cancelled__ = True
        self.close()
        return

    def was_canceled(self):
        return self.__cancelled__

    def on_count_changed(self, value):
        self.__progress__.setValue(value)

    def set_value(self, v):
        self.__progress__.setValue(v)

