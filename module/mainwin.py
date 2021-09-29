from PyQt5 import QtGui, QtWidgets, QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import os
import numpy
import options
import runners
import atomiffileio

class main_window(QtWidgets.QMainWindow):

    def __init__(self):

        self.__runcu_done__ = False
        self.__runcu_carboidxs__ = None 
        self.__runcu_refpoints__ = None
        self.__runcu_weights__ = None
        self.__runcu_pweights__ = None

        self.__runapbs_done__ = False
        self.__runapbs_carboidxs__ = None 
        self.__runapbs_refpoints__ = None
        self.__runapbs_weights__ = None
        self.__runapbs_pweights__ = None

        self.__workdir__ = "./"
        self.__gridbin__ = "./grid"
        self.__fixpdbin__ = "./fixpdb"
        self.__apbsbin__ = "/usr/bin/apbs"
        self.__obabelbin__ = "/usr/bin/obabel"

        self.__plot_done__ = False

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

        self.__savefile_runcu__ = QtWidgets.QAction(QtGui.QIcon("icons/save.png"), "Save CI Coulomb file", self)
        self.__savefile_runcu__.setStatusTip("Save file Coulomb")
        self.__savefile_runcu__.triggered.connect(self.runcu_savefile)
        self.__savefile_runcu__.setEnabled(False)

        self.__savefile_runapbs__ = QtWidgets.QAction(QtGui.QIcon("icons/save.png"), "Save CI APBS file", self)
        self.__savefile_runapbs__.setStatusTip("Save file APBS")
        self.__savefile_runapbs__.triggered.connect(self.runapbs_savefile)
        self.__savefile_runapbs__.setEnabled(False)

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

        runapbs = QtWidgets.QAction(QtGui.QIcon("icons/cancel.png"), "Run APBS Carboi Index", self)
        runapbs.setShortcut("Ctrl+R")
        runapbs.setStatusTip("Run the Carbo index using APBS ")
        runapbs.triggered.connect(self.runapbs)      

        self.statusBar().show()

        menubar = self.menuBar()
        
        file = menubar.addMenu('&File')
        file.addAction(ofile)
        file.addAction(sep)
        file.addAction(self.__savefile_runcu__)
        file.addAction(self.__savefile_runapbs__) 
        file.addAction(sep)
        file.addAction(quit)

        edit = menubar.addMenu('&Edit')
        edit.addAction(config)

        run = menubar.addMenu('&Compute')
        run.addAction(runcu)
        run.addAction(runapbs)

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
        self.__runapbs_dialog__ = runners.runapbsdialog(self)

        self.__workdir__ = self.__configure_dialog__.workdir_line.text()
        self.__gridbin__ = self.__configure_dialog__.gridbin_line.text()
        self.__fixpdbin__ = self.__configure_dialog__.fixpdbin_line.text()
        self.__apbsbin__ = self.__configure_dialog__.apbsbin_line.text()
        self.__obabelbin__ = self.__configure_dialog__.obabelbin_line.text()

    def runapbs (self):
        self.__savefile_runapbs__.setEnabled(False)
        self.__runapbs_done__ = False

        if self.__firstmolsset__ != None and self.__secondmolsset__ != None:
            self.__runapbs_dialog__.setWindowTitle("Run APBS Carbo Index")
            
            self.__runapbs_dialog__.exec()

            stepval = float(self.__runapbs_dialog__.stepval_line.text())
            deltaval = float(self.__runapbs_dialog__.deltaval_line.text())
            exportdx = self.__runapbs_dialog__.exportdxcheckbox.isChecked()
            axis = self.__runapbs_dialog__.axis_line.text()
            
            self.__runapbs_progress_dialog__ = runners.progressdia(self)
            self.__runapbs_progress_dialog__.setWindowModality(QtCore.Qt.WindowModal)
           
            self.__runapbs_progress_dialog__.show()
            self.__runapbs_progress_dialog__.set_value(0)
            self.__runapbs_progress_dialog__.set_title("Run Coulumb")
            self.__runapbs_progress_dialog__.cancel_signal.connect(self.runapbs_cancel)

            self.__calc_apbs__ = runners.run_thread()
            self.__calc_apbs__ .configure (2, False, axis, \
                self.__firstmolsset__, self.__firstmol2file__, self.__firstweightsset__, \
                self.__secondmolsset__, self.__secondmol2file__, self.__secondweightsset__, \
                stepval, deltaval, exportdx, self.__workdir__, \
                self.__runapbs_progress_dialog__, self.__gridbin__ , self.__fixpdbin__ , \
                self.__apbsbin__ , self.__obabelbin__ )
            self.__calc_apbs__.count_changed.connect(self.__runapbs_progress_dialog__.on_count_changed)
            self.__calc_apbs__.finished.connect(self.runapbs_finished)
            self.__calc_apbs__.start()
 
            return

    def runcu (self):

        self.__savefile_runcu__.setEnabled(False)
        self.__runcu_done__ = False

        if self.__firstmolsset__ != None and self.__secondmolsset__ != None:

            self.__runcu_dialog__.setWindowTitle("Run Coulomb Carbo Index")
            
            self.__runcu_dialog__.exec()
           
            stepval = float(self.__runcu_dialog__.stepval_line.text())
            deltaval = float(self.__runcu_dialog__.deltaval_line.text())
            ddieletric = self.__runcu_dialog__.ddielcheckbox.isChecked()
            exportdx = self.__runcu_dialog__.exportdxcheckbox.isChecked()
            axis = self.__runcu_dialog__.axis_line.text()
           
            #print(stepval, deltaval, ddieletric)
           
            self.__runcu_progress_dialog__ = runners.progressdia(self)
            self.__runcu_progress_dialog__.setWindowModality(QtCore.Qt.WindowModal)
           
            self.__runcu_progress_dialog__.show()
            self.__runcu_progress_dialog__.set_value(0)
            self.__runcu_progress_dialog__.set_title("Run Coulumb")
            self.__runcu_progress_dialog__.cancel_signal.connect(self.runcu_cancel)
           
            self.__calc_cu__ = runners.run_thread()
            self.__calc_cu__ .configure (1, ddieletric, axis, \
                self.__firstmolsset__, self.__firstmol2file__, self.__firstweightsset__, \
                self.__secondmolsset__, self.__secondmol2file__, self.__secondweightsset__, \
                stepval, deltaval, exportdx, self.__workdir__, \
                self.__runcu_progress_dialog__)
            self.__calc_cu__.count_changed.connect(self.__runcu_progress_dialog__.on_count_changed)
            self.__calc_cu__.finished.connect(self.runcu_finished)
            self.__calc_cu__.start()
           
        else:
            QtWidgets.QMessageBox.critical( self, \
                    "WARNING", \
                        "No molecules have been specified ") 

    def runapbs_finished(self):
        self.__calc_apbs__.wait()

        self.__runapbs_progress_dialog__.close()

        if self.__calc_apbs__.apbs_is_done():
            return

    def runcu_finished(self):
        self.__calc_cu__.wait()

        self.__runcu_progress_dialog__.close()

        if self.__calc_cu__.cu_is_done():

            carboidxs, refpoints, weights, pweights = self.__calc_cu__.get_carboidxs()
           
            stdev = carboidxs.std(0)
            meanmtx = carboidxs.mean(0)
            
            waverage = numpy.average(carboidxs, 0, weights)
            wvariance = numpy.average((carboidxs-waverage)**2, 0, weights)
            
            pwaverage = numpy.average(carboidxs, 0, pweights)
            pwvariance = numpy.average((carboidxs-waverage)**2, 0, pweights)
           
            if self.__plot_done__ :
                self.__ax__.cla()
                self.__canvas__.draw()
                self.__plot_done__ = False
            else:
                self.__ax__ = self.__figure__.add_subplot(111)
           
            self.__ax__.set_ylim([-1.0, 1.0])
           
            self.__ax__.errorbar(refpoints, meanmtx, stdev,  linestyle='None', \
                marker='^', label="Mean and stdev")
            self.__ax__.plot(refpoints, meanmtx, linestyle='--')
            
            self.__ax__.errorbar(refpoints, waverage, wvariance,  linestyle='None', \
                marker='^', label="Weighted Mean and stdev")
            self.__ax__.plot(refpoints, waverage, linestyle='--')
           
            self.__ax__.errorbar(refpoints, pwaverage, pwvariance,  linestyle='None', \
                marker='^', label="PWeighted Mean and stdev")
            self.__ax__.plot(refpoints, pwaverage, linestyle='--')
           
            self.__ax__.legend(loc="lower left")
           
            self.__canvas__.draw()
            self.__plot_done__ = True
           
            self.__savefile_runcu__.setEnabled(True)
            self.__runcu_done__ = True
           
            self.__runcu_carboidxs__ = carboidxs
            self.__runcu_refpoints__ = refpoints
            self.__runcu_weights__ = weights
            self.__runcu_pweights__ = pweights

    def runapbs_savefile(self):

        if self.__runapbs_done__ :

            name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')

            if (len(name) == 2):
                if (name[0] != ""):
                    return

    def runcu_savefile(self):

        if self.__runcu_done__ :

            name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')

            if (len(name) == 2):
                if (name[0] != ""):
                    carboidxs, refpoints, weights, pweights = self.__calc_cu__.get_carboidxs()
          
                    stdev = carboidxs.std(0)
                    meanmtx = carboidxs.mean(0)
                    
                    waverage = numpy.average(carboidxs, 0, weights)
                    wvariance = numpy.average((carboidxs-waverage)**2, 0, weights)
                    
                    pwaverage = numpy.average(carboidxs, 0, pweights)
                    pwvariance = numpy.average((carboidxs-waverage)**2, 0, pweights)
          
                    file = open(name[0],'w')

                    axis = self.__runcu_dialog__.axis_line.text()
          
                    file.write("%13s %13s %13s %13s %13s %13s %13s\n"%(axis, "SMean",  \
                        "SStdev", "WMean", "WStdev", "PWMean", "PWStdev"))
                    for idx, std in enumerate(stdev):
                        file.write("%+8.6e %+8.6e %+8.6e %+8.6e %+8.6e %+8.6e %+8.6e\n"%(\
                            refpoints[idx], meanmtx[idx] , std, waverage[idx], \
                                wvariance[idx], pwaverage[idx], pwvariance[idx] ))
          
                    file.close()         

    def runcu_cancel(self):

        self.__calc_cu__.m_abort = True
        if not self.__calc_cu__.wait(5000):
            self.__calc_cu__.terminate()
            self.__calc_cu__.quit()
            self.__calc_cu__.wait()

        self.__runcu_progress_dialog__.close()

    def runapbs_cancel(self):

        self.__calc_apbs__.m_abort = True
        if not self.__calc_apbs__.wait(5000):
            self.__calc_apbs__.terminate()
            self.__calc_apbs__.quit()
            self.__calc_apbs__.wait()

        self.__runapbs_progress_dialog__.close()

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
        
        """
        for mol in self.__firstmolsset__:
            print("MOLECULE")
            print(mol)

        print("Second Molecule")
        for mol in self.__secondmolsset__:
            print("MOLECULE")
            print(mol)
        """
        
        self.__runcu_done__ = False
        self.__savefile_runcu__.setEnabled(False)