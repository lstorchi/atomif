from PyQt5 import QtGui, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import options

class main_window(QtWidgets.QMainWindow):

    def __init__(self):

        self.__firstmol2file__ = ""
        self.__secondmol2file__ = ""

        self.__firsttxtfile__ = ""
        self.__secondtxtfile__ = ""

        QtWidgets.QMainWindow.__init__(self) 
        self.resize(640, 480) 
        self.setWindowTitle('ATOMIF')
        self.statusBar().showMessage('ATOMIF started') 

        ofile = QtWidgets.QAction(QtGui.QIcon("icons/open.png"), "Open MOL@ and Weight files", self)
        ofile.setShortcut("Ctrl+O")
        ofile.setStatusTip("Open files")
        ofile.triggered.connect(self.openfiles)

        sep = QtWidgets.QAction(self)
        sep.setSeparator(True)

        quit = QtWidgets.QAction(QtGui.QIcon("icons/cancel.png"), "Quit", self)
        quit.setShortcut("Ctrl+Q")
        quit.setStatusTip("Quit application")
        quit.triggered.connect(self.close)

        self.statusBar().show()

        menubar = self.menuBar()
        
        file = menubar.addMenu('&File')
        file.addAction(ofile)
        file.addAction(quit)

        help = menubar.addMenu('&Help')

        self.__figure__ = plt.figure()
        self.__canvas__ = FigureCanvas(self.__figure__)
        self.__toolbar__ = NavigationToolbar(self.__canvas__, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.__toolbar__)
        layout.addWidget(self.__canvas__)

        maindialog = QtWidgets.QWidget()
        maindialog.setLayout(layout)

        self.setCentralWidget(maindialog)

        self.__options_dialog_files__ = options.optiondialog_files(self)

    def openfiles(self):

        self.__options_dialog_files__.setWindowTitle("Specify filenames")

        self.__options_dialog_files__.exec_()

        self.__firstmol2file__ = \
            self.__options_dialog_files__.firstmol2file_line.text()
        self.__secondmol2file__ = \
            self.__options_dialog_files__.secondmol2file_line.text()

        self.__firsttxtfile__ = \
            self.__options_dialog_files__.firstweigfile_line.text()
        self.__secondtxtfile__ = \
            self.__options_dialog_files__.secondweigfile_line.text()


        

