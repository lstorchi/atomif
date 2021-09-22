from PyQt5 import QtGui, QtWidgets, QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import os
import fields
import options
import runners
import atomiffileio

class main_window(QtWidgets.QMainWindow):

    def __init__(self):

        self.__firstmol2file__ = ""
        self.__firstmolsset__ = None
        self.__secondmol2file__ = ""
        self.__secondmolsset__ = None

        self.__firsttxtfile__ = ""
        self.__firstweightsset__ = None
        self.__secondtxtfile__ = ""
        self.__secondweightsset__ = None

        QtWidgets.QMainWindow.__init__(self) 
        self.resize(640, 480) 
        self.setWindowTitle('ATOMIF')
        self.statusBar().showMessage('ATOMIF started') 

        ofile = QtWidgets.QAction(QtGui.QIcon("icons/open.png"), "Open MOL2 and Weight files", self)
        ofile.setShortcut("Ctrl+O")
        ofile.setStatusTip("Open files")
        ofile.triggered.connect(self.openfiles)

        sep = QtWidgets.QAction(self)
        sep.setSeparator(True)

        quit = QtWidgets.QAction(QtGui.QIcon("icons/cancel.png"), "Quit", self)
        quit.setShortcut("Ctrl+Q")
        quit.setStatusTip("Quit application")
        quit.triggered.connect(self.close)

        config = QtWidgets.QAction(QtGui.QIcon("icons/cancel.png"), "Config", self)
        config.setShortcut("Ctrl+I")
        config.setStatusTip("Configure")
        config.triggered.connect(self.configure)

        runcu = QtWidgets.QAction(QtGui.QIcon("icons/cancel.png"), "Run Coulomb Carboi Index", self)
        runcu.setShortcut("Ctrl+R")
        runcu.setStatusTip("Run the Carbo index using the Coulomb's law ")
        runcu.triggered.connect(self.runcu)      

        self.statusBar().show()

        menubar = self.menuBar()
        
        file = menubar.addMenu('&File')
        file.addAction(ofile)
        file.addAction(quit)

        edit = menubar.addMenu('&Edit')
        edit.addAction(config)

        run = menubar.addMenu('&Compute')
        run.addAction(runcu)

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
        self.__configure_dialog__ = options.configure(self)
        self.__runcu_dialog__ = runners.runcudialog(self)

        self.__workdir__ = self.__configure_dialog__.workdir_line.text()
        self.__gridbin__ = self.__configure_dialog__.gridbin_line.text()
        self.__fixpdbin__ = self.__configure_dialog__.fixpdbin_line.text()
        self.__apbsbin__ = self.__configure_dialog__.apbsbin_line.text()
        self.__obabelbin__ = self.__configure_dialog__.obabelbin_line.text()

    def runcu (self):

        self.__runcu_dialog__.setWindowTitle("Run Coulomb Carbo Index")
        
        self.__runcu_dialog__.exec()

        stepval = float(self.__runcu_dialog__.stepval_line.text())
        deltaval = float(self.__runcu_dialog__.deltaval_line.text())
        ddieletric = self.__runcu_dialog__.ddielcheckbox.isChecked()
        exportdx = self.__runcu_dialog__.exportdxcheckbox.isChecked()

        #print(stepval, deltaval, ddieletric)

        self.__runcu_progress_dialog__ = runners.progressdia(self)
        self.__runcu_progress_dialog__.setWindowModality(QtCore.Qt.WindowModal)

        self.__runcu_progress_dialog__.show()
        self.__runcu_progress_dialog__.set_value(0)
        self.__runcu_progress_dialog__.set_label("Run Coulumb")
        self.__runcu_progress_dialog__.cancel_signal.connect(self.runcu_cancel)

        self.__calc__ = runners.External()
        self.__calc__.countChanged.connect(self.__runcu_progress_dialog__.on_count_changed)
        self.__calc__.finished.connect(self.runcu_finished)
        self.__calc__.start()

        #calc.wait()
        #progress_dialog.close() 

        return

     

    def runcu_finished(self):
        print("in runcu_finished ")
        print("TODO")

        self.__runcu_progress_dialog__.close()

    def runcu_cancel(self, val):

        if val == 1:
            self.__calc__.terminate()

    def configure(self):

        self.__configure_dialog__.setWindowTitle("Configure")

        self.__configure_dialog__.exec()

        self.__workdir__ = self.__configure_dialog__.workdir_line.text()
        if not (os.path.isdir(self.__workdir__ )):
            QtWidgets.QMessageBox.critical( self, \
                    "ERROR", \
                        "Dir " + self.__workdir__  + \
                            " is not a directotory restoring the default value ./ ")
            self.__workdir__ = "./"

        self.__gridbin__ = self.__configure_dialog__.gridbin_line.text()
        if not (os.path.isfile(self.__gridbin__ )):
            QtWidgets.QMessageBox.critical( self, \
                    "ERROR", \
                        "File " + self.__gridbin__  + \
                            " does not exist ")
            self.__gridbin__ = ""

        self.__fixpdbin__ = self.__configure_dialog__.fixpdbin_line.text()
        if not (os.path.isfile(self.__fixpdbin__ )):
            QtWidgets.QMessageBox.critical( self, \
                    "ERROR", \
                        "File " + self.__fixpdbin__  + \
                            " does not exist ")
            self.__fixpdbin__ = ""

        self.__apbsbin__ = self.__configure_dialog__.apbsbin_line.text()
        if not (os.path.isfile(self.__apbsbin__ )):
            QtWidgets.QMessageBox.critical( self, \
                    "ERROR", \
                        "File " + self.__apbsbin__  + \
                            " does not exist ")
            self.__apbsbin__ = ""

        self.__obabelbin__ = self.__configure_dialog__.obabelbin_line.text()
        if not (os.path.isfile(self.__obabelbin__ )):
            QtWidgets.QMessageBox.critical( self, \
                    "ERROR", \
                        "File " + self.__obabelbin__ + \
                            " does not exist ")
            self.__obabelbin__ = ""


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

        for fn in [self.__firstmol2file__ , self.__secondmol2file__, \
            self.__firsttxtfile__ , self.__secondtxtfile__ ]:
            if fn == "":
                return

            if not os.path.isfile(fn):
                QtWidgets.QMessageBox.critical( self, \
                    "ERROR", \
                        "File " + fn + " does not exist")
                return 

        try:
            self.__firstmolsset__ = atomiffileio.mol2atomextractor ( \
                self.__firstmol2file__)
            self.__secondmolsset__ = atomiffileio.mol2atomextractor ( \
                self.__secondmol2file__)
        except Exception as msg:
            self.__firstmolsset__ = None
            self.__secondmolsset__ = None
            QtWidgets.QMessageBox.critical( self, \
                "ERROR", \
                    "error in reading mol2 files " + str(msg))
            return 

        try:
            self.__firstweightsset__ = atomiffileio.extractweight ( \
                self.__firsttxtfile__)
            self.__secondweightsset__ = atomiffileio.extractweight ( \
                self.__secondtxtfile__)
        except Exception as msg:
            self.__firstweightsset__ = None
            self.__secondweightsset__ = None
            QtWidgets.QMessageBox.critical( self, \
                "ERROR", \
                    "error in reading txt files " + str(msg))
            return
        
        if (len(self.__firstmolsset__) != len(self.__firstweightsset__)) or \
            (len(self.__secondweightsset__) != len(self.__secondmolsset__)):
            
            self.__firstmolsset__ = atomiffileio.mol2atomextractor ( \
                self.__firstmol2file__)
            self.__secondmolsset__ = atomiffileio.mol2atomextractor ( \
                self.__secondmol2file__)

            self.__firstweightsset__ = atomiffileio.extractweight ( \
                self.__firsttxtfile__)
            self.__secondweightsset__ = atomiffileio.extractweight ( \
                self.__secondtxtfile__)
 
            QtWidgets.QMessageBox.critical( self, \
                "ERROR", \
                    "Error mismatch between number of weights and number of molecules")
            return

        

