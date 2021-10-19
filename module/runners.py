from PyQt5.QtWidgets import (QDialog, QProgressBar, QPushButton, QGridLayout)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import QtGui, QtWidgets

import os
import carbo
import fields

TYPEOFRUNCOULOMB = 1
TYPEOFRUNAPBS = 2

class runapbsdialog(QtWidgets.QDialog):

    def __init__(self, parent=None):

        super(runapbsdialog, self).__init__(parent)

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

        self.exportdxcheckbox = QtWidgets.QCheckBox("Export DX files ", self)

        self.grid = QtWidgets.QGridLayout(self)
        self.grid.addWidget(stepval_label, 0, 0)
        self.grid.addWidget(self.stepval_line, 0, 1)

        self.grid.addWidget(deltaval_label, 1, 0)
        self.grid.addWidget(self.deltaval_line, 1, 1)

        self.grid.addWidget(axis_label, 2, 0)
        self.grid.addWidget(self.axis_line, 2, 1)

        self.grid.addWidget(self.exportdxcheckbox, 4, 0)

        self.grid.addWidget(self.okbutton, 5, 2)

    def run(self):

        self.close()

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

class run_thread(QThread):
    """
    Runs a counter thread.
    """
    count_changed = pyqtSignal(int)

    __carboidxs__ = None 
    __refpoints__ = None 
    __weights__ = None 
    __pweights__ = None
    __runcu_done__ = False
    __runapbs_done__ = False

    def cu_is_done (self):

        return self.__runcu_done__ 

    def apbs_is_done (self):

        return self.__runapbs_done__ 

    def get_carboidxs (self):

        if self.__runcu_done__  or self.__runapbs_done__:
            return self.__carboidxs__ , \
                self.__refpoints__ , \
                    self.__weights__ , \
                        self.__pweights__
        else:
            return None, None, None, None

    def configure (self, typeofrun, ddieletric, axis, \
        firstmolsset, firstmol2file, firstweightsset, \
        secondmolsset, secondmol2file, secondweightsset, \
        stepval, deltaval, exportdx, workdir, progress,
        gridbin = "", fixpdbin = "", apbsbin = "", obabelbin = ""): 

        self.__gridbin__ = gridbin
        self.__fixpdbin__ = fixpdbin
        self.__apbsbin__ = apbsbin
        self.__obabelbin__ = obabelbin

        self.__type_of_run__ = typeofrun

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

    def run (self):

        self.count_changed.emit(0)

        self.__progress__.set_label("Running first set of molecules")

        cfields1 = None
        allfields1 = None
        gmean1 = None 

        if self.__type_of_run__ == TYPEOFRUNCOULOMB:
            cfields1 = fields.get_cfields(self.__firstmolsset__, self.__stepval__, \
                self.__deltaval__ ,  1.0, False, self.__ddieletric__, \
                    self.count_changed, self.__progress__, 0, 45 )
           
            if (cfields1 != None):
                basename = os.path.splitext(self.__firstmol2file__)[0]
                basename  = basename.split("/")[-1]
           
                if self.__progress__.was_cancelled():
                    return 
           
                gmean1, allfields1 = fields.exporttodx (self.__workdir__ + "/" + basename, \
                         cfields1, self.__firstweightsset__ , self.__stepval__, self.__ddieletric__, \
                            self.__exportdx__, None)
           
            self.count_changed.emit(50)

        elif self.__type_of_run__ == TYPEOFRUNAPBS:
            gmean1, allfields1 = fields.get_apbsfields(self.__obabelbin__, self.__apbsbin__ , \
                self.__exportdx__ , self.__firstmol2file__ , self.__firstweightsset__, \
                    self.__stepval__, self.__deltaval__ , \
                    self.__workdir__ , False, self.count_changed, \
                        self.__progress__, 0, 45 )


        self.count_changed.emit(45)

        self.__progress__.set_label("Running second set of molecules")

        if (allfields1 != None):
           
            if (self.__progress__.was_cancelled()):
              return  

            allfields2 = None
            gmean2 = None 

            if self.__type_of_run__ == TYPEOFRUNCOULOMB:

                cfields2 = fields.get_cfields(self.__secondmolsset__, self.__stepval__, \
                    self.__deltaval__, 1.0, False, self.__ddieletric__, self.count_changed, \
                        self.__progress__, 50, 45 )
            
                if (cfields2 != None):
                    basename = os.path.splitext(self.__secondmol2file__)[0]
                    basename  = basename.split("/")[-1]
            
                    if self.__progress__.was_cancelled():
                        return 
            
                    gmean2, allfields2 = fields.exporttodx (self.__workdir__ + "/" + basename, \
                            cfields2, self.__secondweightsset__ , self.__stepval__, self.__ddieletric__, \
                                self.__exportdx__, \
                                    list(allfields1.values())[0][1]) # fit respect to the first one so we can compute carbo
                
                    self.count_changed.emit(100)
            elif self.__type_of_run__ == TYPEOFRUNAPBS:

                gmean2, allfields2 = fields.get_apbsfields(self.__obabelbin__, self.__apbsbin__ , \
                    self.__exportdx__ , self.__secondmol2file__ , self.__secondweightsset__, \
                        self.__stepval__, self.__deltaval__ , \
                        self.__workdir__ , False, self.count_changed, \
                            self.__progress__, 50, 45, list(allfields1.values())[0][1]) 

                self.count_changed.emit(100)

        if (allfields1 != None) and (allfields2 != None):
            # compute carbo
            self.__progress__.set_title("Compute Carbo index")

            self.__progress__.set_label("Computing Carbo index alog " +  \
                self.__axis__ + " axis")

            self.count_changed.emit(0)

            """
            for k in allfields1:
                print(k, allfields1[k][1].grid.shape)

            for k in allfields2:
                print(k, allfields2[k][1].grid.shape)
            """

            try:
                self.__carboidxs__, self.__refpoints__, self.__weights__, self.__pweights__ = \
                  carbo.returncarbodxs(allfields1, allfields2, False, self.__axis__, \
                      self.count_changed, self.__progress__)

                self.count_changed.emit(100)

                if self.__type_of_run__ == TYPEOFRUNCOULOMB:
                    self.__runcu_done__ = True
                elif self.__type_of_run__ == TYPEOFRUNAPBS:
                    self.__runapbs_done__ = True

                #print(self.__carboidxs__, self.__refpoints__, self.__weights__, self.__pweights__)

            except Exception as exp:
                self.__carboidxs__ = None 
                self.__refpoints__ = None 
                self.__weights__ = None 
                self.__pweights__ = None
                
                QtWidgets.QMessageBox.critical( self, \
                    "ERROR", exp) 

        
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
