from PyQt5 import QtGui, QtWidgets, QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import os
import fields
import options
import runners
import progressdia
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

        progress_dialog = progressdia.progressdia(self)
        #progress_dialog.setWindowModality(QtCore.Qt.WindowModal)

        progress_dialog.show()
        progress_dialog.set_value(0)
        progress_dialog.set_label("Test")

        self.calc = progressdia.External()
        self.calc.countChanged.connect(progress_dialog.on_count_changed)
        self.calc.start()

        #calc.wait()


        if (progress_dialog.was_canceled()):
          return  

        #progress_dialog.close() 
        return

        #cfields1 = fields.get_cfields(self.__firstmolsset__, stepval, deltaval, \
        #    1.0, False, ddieletric, progress_dialog)

        gmean1 = None 
        allfields1 = None

        progress_dialog.setLabelText("Computing DXes")
        progress_dialog.set_value(0)
        progress_dialog.setAutoClose(False)
        progress_dialog.setAutoReset(True)
        progress_dialog.setMinimumDuration(0)

        if (cfields1 != None):
            basename = os.path.splitext(self.__firstmol2file__)[0]
            basename  = basename.split("/")[-1]

            gmean1, allfields1 = fields.exporttodx (self.__workdir__ + "/" + basename, \
                     cfields1, self.__firstweightsset__ , stepval, ddieletric, \
                         exportdx)

        progress_dialog.setValue(100)

        gmean2 = None 
        allfields2 = None

        if (cfields1 != None):
            progress_dialog.setLabelText("Computing Coulomb molecule " + \
                self.__secondmol2file__) 
            
            progress_dialog.setValue(0)
            
            if (progress_dialog.was_canceled()):
              return  
            
            cfields2 = fields.get_cfields(self.__secondmolsset__, stepval, deltaval, \
                1.0, False, ddieletric, progress_dialog)

            progress_dialog.setLabelText("Computing DXes")
            progress_dialog.setValue(0)
            
            if (cfields2 != None):
                basename = os.path.splitext(self.__secondmol2file__)[0]
                basename  = basename.split("/")[-1]
            
                gmean2, allfields2 = fields.exporttodx (self.__workdir__ + "/" + basename, \
                        cfields2, self.__secondweightsset__ , stepval, ddieletric, \
                            exportdx)
            
            progress_dialog.setValue(100)

        progress_dialog.close()

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

        

