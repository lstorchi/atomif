from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import os
import numpy
import options
import runners
import atomiffileio
import runnersdialog

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])


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

        self.__runmifprofiles_done__ = False

        self.__runmifinteraction_done__ = False

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

        self.__savefile_runmifprofiles__ = QtWidgets.QAction(QtGui.QIcon("icons/save.png"), "Save MIF profiles file", self)
        self.__savefile_runmifprofiles__.setStatusTip("Save file MIF Profiles")
        self.__savefile_runmifprofiles__.triggered.connect(self.runmifprofiles_savefile)
        self.__savefile_runmifprofiles__.setEnabled(False)

        self.__savefile_runmifinteraction__ = QtWidgets.QAction(QtGui.QIcon("icons/save.png"), "Save MIF Interaction file", self)
        self.__savefile_runmifinteraction__.setStatusTip("Save file MIF Interaction")
        self.__savefile_runmifinteraction__.triggered.connect(self.runmifinteraction_savefile)
        self.__savefile_runmifinteraction__.setEnabled(False)

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

        runcu_ico = QtWidgets.QAction(QtGui.QIcon("icons/cancel.png"), "Run Coulomb Carbo Index", self)
        runcu_ico.setStatusTip("Run the Carbo index using the Coulomb's law ")
        runcu_ico.triggered.connect(self.runcu)      

        runapbs_ico = QtWidgets.QAction(QtGui.QIcon("icons/cancel.png"), "Run APBS Carbo Index", self)
        runapbs_ico.setStatusTip("Run the Carbo index using APBS ")
        runapbs_ico.triggered.connect(self.runapbs)      

        runmifprofiles_ico = QtWidgets.QAction(QtGui.QIcon("icons/cancel.png"), "Run MIF Profiles", self)
        runmifprofiles_ico.setStatusTip("Run the MIF profiles ")
        runmifprofiles_ico.triggered.connect(self.runmifprofiles)      
       
        runmifinteraction_ico = QtWidgets.QAction(QtGui.QIcon("icons/cancel.png"), "Run MIF Interaction", self)
        runmifinteraction_ico.setStatusTip("Run the MIF Interaction procedure ")
        runmifinteraction_ico.triggered.connect(self.runmifinteraction)      

        self.statusBar().show()

        menubar = self.menuBar()
        
        file = menubar.addMenu('&File')
        file.addAction(ofile)
        file.addAction(sep)
        file.addAction(self.__savefile_runcu__)
        file.addAction(self.__savefile_runapbs__) 
        file.addAction(self.__savefile_runmifprofiles__)
        file.addAction(self.__savefile_runmifinteraction__)
        file.addAction(sep)
        file.addAction(quit)

        edit = menubar.addMenu('&Edit')
        edit.addAction(config)

        run = menubar.addMenu('&Compute')
        run.addAction(runcu_ico)
        run.addAction(runapbs_ico)
        run.addAction(runmifprofiles_ico)
        run.addAction(runmifinteraction_ico)

        help = menubar.addMenu('&Help')

        self.__figure__ = plt.figure()
        self.__canvas__ = FigureCanvas(self.__figure__)
        self.__toolbar__ = NavigationToolbar(self.__canvas__, self)

        self.__qtable__ = QtWidgets.QTableView (self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.__toolbar__)
        layout.addWidget(self.__canvas__)
        layout.addWidget(self.__qtable__)

        maindialog = QtWidgets.QWidget()
        maindialog.setLayout(layout)

        self.setCentralWidget(maindialog)

        self.__options_dialog_files__ = options.optiondialog_files(self)
        self.__configure_dialog__ = options.configure(self)
        self.__runcu_dialog__ = runnersdialog.runcudialog(self)
        self.__runapbs_dialog__ = runnersdialog.runapbsdialog(self)
        self.__runmifprofiles_dialog__ = runnersdialog.runmifprofilesdialog(self)
        self.__runmifinteraction_dialog__ = runnersdialog.runmifinteractiondialog(self)

        self.__workdir__ = self.__configure_dialog__.workdir_line.text()
        self.__gridbin__ = self.__configure_dialog__.gridbin_line.text()
        self.__fixpdbin__ = self.__configure_dialog__.fixpdbin_line.text()
        self.__apbsbin__ = self.__configure_dialog__.apbsbin_line.text()
        self.__obabelbin__ = self.__configure_dialog__.obabelbin_line.text()

    def runmifinteraction (self):
        self.__savefile_runmifinteraction__.setEnabled(False)
        self.__runmifinteraction_done__ = False
        self.__mifitecationdata__ = None

        if self.__firstmolsset__ != None and self.__secondmolsset__ != None:
            self.__runmifprofiles_dialog__.setWindowTitle("Run MIF profiles")
            
            self.__runmifinteraction_dialog__.exec()

            stepval = float(self.__runmifinteraction_dialog__.stepval_line.text())
            deltaval = float(self.__runmifinteraction_dialog__.deltaval_line.text())
            probe = self.__runmifinteraction_dialog__.probe_line.text()
            minimaselection = self.__runmifinteraction_dialog__.minima_line.text()
            
            self.__runmifinteraction_progress_dialog__ = runnersdialog.progressdia(self)
            self.__runmifinteraction_progress_dialog__.setWindowModality(QtCore.Qt.WindowModal)
           
            self.__runmifinteraction_progress_dialog__.show()
            self.__runmifinteraction_progress_dialog__.set_value(0)
            self.__runmifinteraction_progress_dialog__.set_title("Run Grid Interaction")
            self.__runmifinteraction_progress_dialog__.cancel_signal.connect(self.runmifinteraction_cancel)

            self.__calc_mifinteraction__ = runners.run_thread_mifinteraction()
            self.__calc_mifinteraction__ .configure (self.__firstmolsset__, self.__firstmol2file__, \
                self.__firstweightsset__, self.__secondmolsset__, self.__secondmol2file__, \
                self.__secondweightsset__, stepval, deltaval, probe, minimaselection, self.__workdir__, \
                self.__runmifinteraction_progress_dialog__, self.__runmifinteraction_dialog__.kontcheckbox.isChecked(), \
                self.__gridbin__ , self.__fixpdbin__ , self.__apbsbin__ , self.__obabelbin__ )

            self.__calc_mifinteraction__.count_changed.connect(self.__runmifinteraction_progress_dialog__.on_count_changed)
            self.__calc_mifinteraction__.finished.connect(self.runmifinteraction_finished)
            self.__calc_mifinteraction__.start()
 
            return

    def runmifprofiles (self):
        self.__savefile_runmifprofiles__.setEnabled(False)
        self.__runmifprofiles_done__ = False

        if self.__firstmolsset__ != None and self.__secondmolsset__ != None:
            self.__runmifprofiles_dialog__.setWindowTitle("Run MIF profiles")
            
            self.__runmifprofiles_dialog__.exec()

            stepval = float(self.__runmifprofiles_dialog__.stepval_line.text())
            deltaval = float(self.__runmifprofiles_dialog__.deltaval_line.text())
            #exportdx = self.__runapbs_dialog__.exportdxcheckbox.isChecked()
            axis = self.__runmifprofiles_dialog__.axis_line.text()
            probe = self.__runmifprofiles_dialog__.probe_line.text()
            minimaselection = self.__runmifprofiles_dialog__.minima_line.text()
            
            self.__runmifprofiles_progress_dialog__ = runnersdialog.progressdia(self)
            self.__runmifprofiles_progress_dialog__.setWindowModality(QtCore.Qt.WindowModal)
           
            self.__runmifprofiles_progress_dialog__.show()
            self.__runmifprofiles_progress_dialog__.set_value(0)
            self.__runmifprofiles_progress_dialog__.set_title("Run Grid Profiles")
            self.__runmifprofiles_progress_dialog__.cancel_signal.connect(self.runmifprofiles_cancel)

            self.__calc_mifprofiles__ = runners.run_thread_mif()
            self.__calc_mifprofiles__ .configure (self.__firstmolsset__, self.__firstmol2file__, \
                self.__firstweightsset__, self.__secondmolsset__, self.__secondmol2file__, \
                self.__secondweightsset__, stepval, deltaval, axis, probe, minimaselection, self.__workdir__, \
                self.__runmifprofiles_progress_dialog__, self.__runmifprofiles_dialog__.kontcheckbox.isChecked(), \
                self.__gridbin__ , self.__fixpdbin__ , self.__apbsbin__ , self.__obabelbin__ )

            self.__calc_mifprofiles__.count_changed.connect(self.__runmifprofiles_progress_dialog__.on_count_changed)
            self.__calc_mifprofiles__.finished.connect(self.runmifprofiles_finished)
            self.__calc_mifprofiles__.start()
 
            return
 
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
            
            self.__runapbs_progress_dialog__ = runnersdialog.progressdia(self)
            self.__runapbs_progress_dialog__.setWindowModality(QtCore.Qt.WindowModal)
           
            self.__runapbs_progress_dialog__.show()
            self.__runapbs_progress_dialog__.set_value(0)
            self.__runapbs_progress_dialog__.set_title("Run Coulumb")
            self.__runapbs_progress_dialog__.cancel_signal.connect(self.runapbs_cancel)

            self.__calc_apbs__ = runners.run_thread_ci()
            self.__calc_apbs__ .configure (runners.TYPEOFRUNAPBS, False, axis, \
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
           
            self.__runcu_progress_dialog__ = runnersdialog.progressdia(self)
            self.__runcu_progress_dialog__.setWindowModality(QtCore.Qt.WindowModal)
           
            self.__runcu_progress_dialog__.show()
            self.__runcu_progress_dialog__.set_value(0)
            self.__runcu_progress_dialog__.set_title("Run Coulumb")
            self.__runcu_progress_dialog__.cancel_signal.connect(self.runcu_cancel)
           
            self.__calc_cu__ = runners.run_thread_ci()
            self.__calc_cu__ .configure (runners.TYPEOFRUNCOULOMB, ddieletric, axis, \
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

    def runmifinteraction_finished(self):
        self.__calc_mifinteraction__.wait()

        self.__runmifinteraction_progress_dialog__.close()

        if self.__calc_mifinteraction__.mif_is_done():

            firstset, secondset = self.__calc_mifinteraction__.get_results()

            self.__mifitecationdata__ = []

            for index in range(len(firstset)):
                 miffilename = "MIF of " + self.__secondmol2file__ 
                 coordfilename = "Molecule " + str(index) + " of " + \
                     self.__firstmol2file__ 

                 counter = firstset[index]["counter"]
                 counter_multiple = firstset[index]["counter_multiple"]
                 peratom_counter = firstset[index]["peratom_counter"]          
                 peratom_counter_multiple = firstset[index]["peratom_counter_multiple"]  

                 self.__mifitecationdata__.append(\
                     [miffilename, coordfilename, counter, counter_multiple])
                
                 #print(miffilename, " ", coordfilename, " ,", counter, " , " , counter_multiple)
                
                 sum = 0
                 sum_multiple = 0
                 for ai in range(len(peratom_counter_multiple)):
                     if (peratom_counter_multiple[ai] != 0 and \
                         peratom_counter[ai] != 0):
                        self.__mifitecationdata__.append(["Atom", ai+1, peratom_counter_multiple[ai], 
                          peratom_counter[ai] ])
                     #print("atom , ", ai+1, " , ", peratom_counter_multiple[ai], " , ", \
                     #   peratom_counter[ai])
                     sum_multiple += peratom_counter_multiple[ai]
                     sum += peratom_counter[ai]
                
                 if sum_multiple != counter_multiple:
                     print("Error in Tot: ", sum_multiple, " vs ", counter_multiple)
                
                 if sum != counter:
                     print("Error in Tot: ", sum, " vs ", counter)
            
            for index in range(len(secondset)):
                 miffilename = "MIF of " + self.__firstmol2file__
                 coordfilename = "Molecule " + str(index) + " of " + \
                     self.__secondmol2file__

                 counter = secondset[index]["counter"]
                 counter_multiple = secondset[index]["counter_multiple"]
                 peratom_counter = secondset[index]["peratom_counter"]          
                 peratom_counter_multiple = secondset[index]["peratom_counter_multiple"]  

                 self.__mifitecationdata__.append([miffilename, coordfilename, counter, counter_multiple])
                
                 #print(miffilename, " ", coordfilename, " ,", counter, " , " , counter_multiple)
                
                 sum = 0
                 sum_multiple = 0
                 for ai in range(len(peratom_counter_multiple)):
                     if (peratom_counter_multiple[ai] != 0 and \
                         peratom_counter[ai] != 0):
                        self.__mifitecationdata__.append(["Atom", ai+1, peratom_counter_multiple[ai], 
                          peratom_counter[ai] ])
                     #print("atom , ", ai+1, " , ", peratom_counter_multiple[ai], " , ", \
                     #   peratom_counter[ai])
                     sum_multiple += peratom_counter_multiple[ai]
                     sum += peratom_counter[ai]
                
                 if sum_multiple != counter_multiple:
                     print("Error in Tot: ", sum_multiple, " vs ", counter_multiple)
                
                 if sum != counter:
                     print("Error in Tot: ", sum, " vs ", counter)

            self.__savefile_runmifinteraction__.setEnabled(True)

            self.__qtable__.clearSpans()

            model = TableModel(self.__mifitecationdata__)
            self.__qtable__.setModel(model)
            self.__runmifinteraction_done__ = True

        return

    def runmifprofiles_finished(self):
        self.__calc_mifprofiles__.wait()

        self.__runmifprofiles_progress_dialog__.close()

        if self.__calc_mifprofiles__.mif_is_done():

            values1, values2 = self.__calc_mifprofiles__.get_results()

            xval1 = []
            yval1 = []
            for v in values1:
                xval1.append(v[0])
                yval1.append(v[3])

            xval2 = []
            yval2 = []
            for v in values2:
                xval2.append(v[0])
                yval2.append(v[3])

            if self.__plot_done__ :
                self.__ax__.cla()
                self.__canvas__.draw()
                self.__plot_done__ = False
            else:
                self.__ax__ = self.__figure__.add_subplot(111)
           
            #self.__ax__.set_ylim([-1.0, 1.0])
           
            #self.__ax__.errorbar(refpoints, meanmtx, stdev,  linestyle='None', \
            #    marker='^', label="Mean and stdev")
            self.__ax__.plot(xval1, yval1, linestyle='--', label="First mol set")
            
            #self.__ax__.errorbar(refpoints, waverage, wvariance,  linestyle='None', \
            #    marker='^', label="Weighted Mean and stdev")
            self.__ax__.plot(xval2, yval2, linestyle='--', label="Second mol set")
           
            self.__ax__.legend(loc="lower left")
           
            self.__canvas__.draw()
            self.__plot_done__ = True
           
            self.__savefile_runmifprofiles__.setEnabled(True)
            self.__runmifprofiles_done__ = True
           
            self.__mifprofiles_value1__ = values1
            self.__mifprofiles_value2__ = values2


    def runapbs_finished(self):
        self.__calc_apbs__.wait()

        self.__runapbs_progress_dialog__.close()

        if self.__calc_apbs__.apbs_is_done():
            carboidxs, refpoints, weights, pweights = self.__calc_apbs__.get_carboidxs()
           
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
           
            self.__savefile_runapbs__.setEnabled(True)
            self.__runapbs_done__ = True
           
            self.__runapsb_carboidxs__ = carboidxs
            self.__runapsb_refpoints__ = refpoints
            self.__runapsb_weights__ = weights
            self.__runapsb_pweights__ = pweights

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

    def runmifinteraction_savefile(self):

        if self.__runmifinteraction_done__:

            name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
           
            if (len(name) == 2):
                if (name[0] != ""):
            
                    file = open(name[0],'w')

                    for val in self.__mifitecationdata__:
                        file.write(str(val[0]) + " , " + str(val[1]) + \
                            " , " + str(val[2]) + " , " + str(val[3]) + "\n")
           
                    file.close()         
        return

    def runmifprofiles_savefile(self):

        if self.__runmifprofiles_done__ :

            name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')

            if (len(name) == 2):
                if (name[0] != ""):
          
                    file = open(name[0],'w')

                    self.__mifprofiles_value1__
                    self.__mifprofiles_value2__

                    axis = self.__runmifprofiles_dialog__.axis_line.text()
                    file.write(self.__firstmol2file__+"\n")
                    file.write("%13s %13s %13s %13s %13s\n"%(axis, "CountLower",  \
                        "Count", "SumE", "AvgE"))
                    for v in self.__mifprofiles_value1__:
                        file.write("%+8.6e %+8.6e %+8.6e %+8.6e %+8.6e\n"%(\
                            v[0], v[1], v[2], v[3], v[4]))

                    file.write(self.__secondmol2file__+"\n")
                    file.write("%13s %13s %13s %13s %13s\n"%(axis, "CountLower",  \
                        "Count", "SumE", "AvgE"))
                    for v in self.__mifprofiles_value2__:
                        file.write("%+8.6e %+8.6e %+8.6e %+8.6e %+8.6e\n"%(\
                            v[0], v[1], v[2], v[3], v[4]))
          
                    file.close()         
            return

    def runapbs_savefile(self):

        if self.__runapbs_done__ :

            name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')

            if (len(name) == 2):
                if (name[0] != ""):
                    carboidxs, refpoints, weights, pweights = self.__calc_apbs__.get_carboidxs()
          
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

    def runmifinteraction_cancel(self):
        
        self.__calc_mifinteraction__.m_abort = True
        if not self.__calc_mifinteraction__.wait(5000):
            self.__calc_mifinteraction__.terminate()
            self.__calc_mifinteraction__.quit()
            self.__calc_mifinteraction__.wait()

        self.__runmifinteraction_progress_dialog__.close()

    def runmifprofiles_cancel(self):

        self.__calc_mifprofiles__.m_abort = True
        if not self.__calc_mifprofiles__.wait(5000):
            self.__calc_mifprofiles__.terminate()
            self.__calc_mifprofiles__.quit()
            self.__calc_mifprofiles__.wait()

        self.__runmifprofiles_progress_dialog__.close()

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