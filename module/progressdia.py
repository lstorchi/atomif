from PyQt5.QtWidgets import (QDialog, QProgressBar, QPushButton, QGridLayout)

from PyQt5.QtCore import QThread, pyqtSignal

import time

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
            time.sleep(1)
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
        self.grid.addWidget(self.__button__, 1, 1)

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

