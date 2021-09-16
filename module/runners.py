from PyQt5 import QtGui, QtWidgets

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

        self.grid = QtWidgets.QGridLayout(self)
        self.grid.addWidget(stepval_label, 0, 0)
        self.grid.addWidget(self.stepval_line, 0, 1)

        self.grid.addWidget(deltaval_label, 1, 0)
        self.grid.addWidget(self.deltaval_line, 1, 1)

        self.grid.addWidget(self.ddielcheckbox, 2, 0)

        self.grid.addWidget(self.okbutton, 3, 2)

    def run(self):

        self.close()