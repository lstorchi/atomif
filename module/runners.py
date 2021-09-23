from PyQt5.QtWidgets import (QDialog, QProgressBar, QPushButton, QGridLayout)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import QtGui, QtWidgets

import os
import carbo
import fields

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

        axis_label = QtWidgets.QLabel("Axis : ", self)
        self.axis_line = QtWidgets.QLineEdit("x", self)
        self.axis_line.move(20, 20)
        self.axis_line.resize(280,40)

        self.ddielcheckbox = QtWidgets.QCheckBox("Enable Dielectric damping ", self)

        self.exportdxcheckbox = QtWidgets.QCheckBox("Export DX files ", self)

        self.grid = QtWidgets.QGridLayout(self)
        self.grid.addWidget(stepval_label, 0, 0)
        self.grid.addWidget(self.stepval_line, 0, 1)

        self.grid.addWidget(deltaval_label, 1, 0)
        self.grid.addWidget(self.deltaval_line, 1, 1)

        self.grid.addWidget(axis_label, 2, 0)
        self.grid.addWidget(self.axis_line, 2, 1)

        self.grid.addWidget(self.ddielcheckbox, 3, 0)
        self.grid.addWidget(self.exportdxcheckbox, 4, 0)

        self.grid.addWidget(self.okbutton, 5, 2)

    def run(self):

        self.close()

class runcu_thread(QThread):
    """
    Runs a counter thread.
    """
    count_changed = pyqtSignal(int)

    __carboidxs__ = None 
    __refpoints__ = None 
    __weights__ = None 
    __pweights__ = None
    __done__ = False

    def get_carboidxs (self):

        if self.__done__ :
            return self.__carboidxs__ , \
                self.__refpoints__ , \
                    self.__weights__ , \
                        self.__pweights__

    def configure (self, ddieletric, axis, \
        firstmolsset, firstmol2file, firstweightsset, \
        secondmolsset, secondmol2file, secondweightsset, \
        stepval, deltaval, exportdx, workdir, progress): 

        self.__ddieletric__ = ddieletric
        self.__axis__ = axis

        self.__firstmolsset__ = firstmolsset
        self.__firstmol2file__ = firstmol2file
        self.__firstweightsset__ = firstweightsset

        self.__secondmolsset__ = secondmolsset
        self.__secondmol2file__ = secondmol2file
        self.__secondweightsset__ = secondweightsset

        self.__stepval__ = stepval
        self.__deltaval__ = deltaval
        self.__exportdx__ = exportdx
        self.__workdir__ = workdir

        self.__progress__ = progress

    def run(self):

        self.count_changed.emit(0)

        self.__progress__.set_label("Running first set of molecules")

        self.__cfields1__ = fields.get_cfields(self.__firstmolsset__, self.__stepval__, \
            self.__deltaval__ ,  1.0, False, self.__ddieletric__, \
                self.count_changed, self.__progress__, 0, 45 )

        if self.__progress__.was_cancelled():
            return 

        self.count_changed.emit(45)

        self.__gmean1__ = None 
        self.__allfields1__ = None

        if (self.__cfields1__ != None):
            basename = os.path.splitext(self.__firstmol2file__)[0]
            basename  = basename.split("/")[-1]

            if self.__progress__.was_cancelled():
                return 

            self.__gmean1__, self.__allfields1__ = fields.exporttodx (self.__workdir__ + "/" + basename, \
                     self.__cfields1__, self.__firstweightsset__ , self.__stepval__, self.__ddieletric__, \
                        self.__exportdx__, None)

        self.count_changed.emit(50)

        self.__gmean2__ = None 
        self.__allfields2__ = None

        self.__progress__.set_label("Running second set of molecules")

        if (self.__allfields1__ != None):
            
            if (self.__progress__.was_cancelled()):
              return  

            self.__cfields2__ = fields.get_cfields(self.__secondmolsset__, self.__stepval__, \
                self.__deltaval__, 1.0, False, self.__ddieletric__, self.count_changed, \
                    self.__progress__, 50, 45 )

            if (self.__cfields2__ != None):
                basename = os.path.splitext(self.__secondmol2file__)[0]
                basename  = basename.split("/")[-1]

                if self.__progress__.was_cancelled():
                    return 

                self.__gmean2__, self.__allfields2__ = fields.exporttodx (self.__workdir__ + "/" + basename, \
                        self.__cfields2__, self.__secondweightsset__ , self.__stepval__, self.__ddieletric__, \
                            self.__exportdx__, \
                                list(self.__allfields1__.values())[0][1]) # fit respect to the first one so we can compute carbo
            
                self.count_changed.emit(100)

                self.__done__ = True

        if (self.__allfields1__ != None) and (self.__allfields2__ != None):
            # compute carbo
            self.__progress__.set_title("Compute Carbo index")

            self.__progress__.set_label("Computing Carbo index alog " +  \
                self.__axis__ + " axis")

            self.count_changed.emit(0)

            try:
                self.__carboidxs__, self.__refpoints__, self.__weights__, self.__pweights__ = \
                  carbo.returncarbodxs(self.__allfields1__, self.__allfields2__, False, self.__axis__, \
                      self.count_changed, self.__progress__)

                self.count_changed.emit(100)
                  
                #stdev = carboidxs.std(0)
                #meanmtx = carboidxs.mean(0)
               
                #waverage = numpy.average(carboidxs, 0, weights)
                #wvariance = numpy.average((carboidxs-waverage)**2, 0, weights)
            except Exception as exp:
                self.__carboidxs__ = None 
                self.__refpoints__ = None 
                self.__weights__ = None 
                self.__pweights__ = None
                
                QtWidgets.QMessageBox.critical( self, \
                    "ERROR", \
                        exp) 

        
class progressdia (QDialog):

    cancel_signal = pyqtSignal()

    def __init__(self, parent=None):

        super(progressdia, self).__init__(parent)

        self.__cancelled__ = False       
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Progress Bar')

        self.__label__ = QtWidgets.QLabel("Starting ..,", self)

        self.__progress__ = QProgressBar(self)
        self.__progress__.setGeometry(0, 0, 300, 25)
        self.__progress__.setMaximum(100)

        self.__cancel_button__ = QPushButton('Cancel', self)
        self.__cancel_button__.move(0, 30)
        self.__cancel_button__.clicked.connect(self.cancel_func)

        self.grid = QGridLayout(self)
 
        self.grid.addWidget(self.__label__, 0, 0)
        self.grid.addWidget(self.__progress__ , 1, 0)
        self.grid.addWidget(self.__cancel_button__, 2, 0)

    def set_label(self, label):
        self.__label__.setText(label)

    def set_title (self, text):
        self.setWindowTitle(text)

    def cancel_func (self):
        self.__cancelled__ = True
        self.cancel_signal.emit()

    def was_cancelled(self):
        return self.__cancelled__

    def on_count_changed(self, value):
        self.__progress__.setValue(value)

    def set_value(self, value):
        self.__progress__.setValue(value)
