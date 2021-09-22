from PyQt5.QtWidgets import (QDialog, QProgressBar, QPushButton, QGridLayout)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import QtGui, QtWidgets

import time

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

class runcu_thread(QThread):
    """
    Runs a counter thread.
    """
    countChanged = pyqtSignal(int)

    def configure (self, ddieletric, firstmolsset, stepval, deltaval, \
        progress_dialog, exportdx): 

        self.__ddieletric__ = ddieletric
        self.__firstmolsset__ = firstmolsset
        self.__stepval__ = stepval
        self.__deltaval__ = deltaval
        self.__progress_dialog__ = progress_dialog
        self.__exportdx__ = exportdx

    def run(self):
        
        cfields1 = fields.get_cfields(self.__firstmolsset__, stepval, deltaval, \
            1.0, False, ddieletric, progress_dialog)

        gmean1 = None 
        allfields1 = None

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
        count = 0
        while count < TIME_LIMIT:
            count +=1
            time.sleep(0.1)
            self.countChanged.emit(count)

            print(count)


class progressdia (QDialog):

    cancel_signal = pyqtSignal(int)

    def __init__(self, parent=None):

        super(progressdia, self).__init__(parent)
        
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Progress Bar')
        self.__progress__ = QProgressBar(self)
        self.__progress__.setGeometry(0, 0, 300, 25)
        self.__progress__.setMaximum(100)

        self.__cancel_button__ = QPushButton('Cancel', self)
        self.__cancel_button__.move(0, 30)
        self.__cancel_button__.clicked.connect(self.cancel_func)

        self.grid = QGridLayout(self)

        self.grid.addWidget(self.__progress__ , 0, 0)
        self.grid.addWidget(self.__cancel_button__, 1, 0)

    def set_label(self, label):
        self.setWindowTitle(label)

    def cancel_func (self):
        self.cancel_signal.emit(1)
        self.close()

    def on_count_changed(self, value):
        self.__progress__.setValue(value)

    def set_value(self, v):
        self.__progress__.setValue(v)
