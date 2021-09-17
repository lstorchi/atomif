from PyQt5 import QtGui, QtWidgets

class optiondialog_files(QtWidgets.QDialog):

    def __init__(self, parent=None):

        super(optiondialog_files, self).__init__(parent)

        self.okbutton = QtWidgets.QPushButton('Ok')
        self.okbutton.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        self.okbutton.clicked.connect(self.closedialog)

        firstmol2file_label = QtWidgets.QLabel("First Multi-mol2:", self)
        self.firstmol2file_line = QtWidgets.QLineEdit("", self)
        self.firstmol2file_line.move(20, 20)
        self.firstmol2file_line.resize(280,40)
        firstmol2file_button = QtWidgets.QPushButton("Browse")
        firstmol2file_button.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        firstmol2file_button.clicked.connect (self.browsefirstmol2)
        firstweigfile_label = QtWidgets.QLabel("Weight:", self)
        self.firstweigfile_line = QtWidgets.QLineEdit("", self)
        self.firstweigfile_line.move(20, 20)
        self.firstweigfile_line.resize(280,40)
        firstweigfile_button = QtWidgets.QPushButton("Browse")
        firstweigfile_button.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        firstweigfile_button.clicked.connect (self.browsefirstweig)

        secondmol2file_label = QtWidgets.QLabel("Second Multi-mol2:", self)
        self.secondmol2file_line = QtWidgets.QLineEdit("", self)
        self.secondmol2file_line.move(20, 20)
        self.secondmol2file_line.resize(280,40)
        secondmol2file_button = QtWidgets.QPushButton("Browse")
        secondmol2file_button.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        secondmol2file_button.clicked.connect (self.browsesecondmol2)
        secondweigfile_label = QtWidgets.QLabel("Weight:", self)
        self.secondweigfile_line = QtWidgets.QLineEdit("", self)
        self.secondweigfile_line.move(20, 20)
        self.secondweigfile_line.resize(280,40)
        secondweigfile_button = QtWidgets.QPushButton("Browse")
        secondweigfile_button.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        secondweigfile_button.clicked.connect (self.browsesecondweig)

        self.grid = QtWidgets.QGridLayout(self)

        self.grid.addWidget(firstmol2file_label, 0, 0)
        self.grid.addWidget(self.firstmol2file_line, 0, 1)
        self.grid.addWidget(firstmol2file_button, 0, 2)
        self.grid.addWidget(firstweigfile_label, 0, 3)
        self.grid.addWidget(self.firstweigfile_line, 0, 4)
        self.grid.addWidget(firstweigfile_button, 0, 5)

        self.grid.addWidget(secondmol2file_label, 1, 0)
        self.grid.addWidget(self.secondmol2file_line, 1, 1)
        self.grid.addWidget(secondmol2file_button, 1, 2)
        self.grid.addWidget(secondweigfile_label, 1, 3)
        self.grid.addWidget(self.secondweigfile_line, 1, 4)
        self.grid.addWidget(secondweigfile_button, 1, 5)

        self.grid.addWidget(self.okbutton, 2, 5)

    def closedialog(self):
        self.close()

    def browsefirstmol2(self):

        mol2 = QtWidgets.QFileDialog.getOpenFileName(self,
                "Open File", "./", "mol2 (*.mol2)")[0]
        self.firstmol2file_line.clear()
        self.firstmol2file_line.insert (mol2)

    def browsesecondmol2(self):

        mol2 = QtWidgets.QFileDialog.getOpenFileName(self,
                "Open File", "./", "mol2 (*.mol2)")[0]
        self.secondmol2file_line.clear()
        self.secondmol2file_line.insert (mol2)
 
    def browsefirstweig(self):

        weig = QtWidgets.QFileDialog.getOpenFileName(self,
                "Open File", "./", "txt (*.txt)")[0]
        self.firstweigfile_line.clear()      
        self.firstweigfile_line.insert (weig)

    def browsesecondweig(self):

        weig = QtWidgets.QFileDialog.getOpenFileName(self,
                "Open File", "./", "txt (*.txt)")[0]
        self.secondweigfile_line.clear()                
        self.secondweigfile_line.insert (weig)
 
class configure(QtWidgets.QDialog):

    def __init__(self, parent=None):

        super(configure, self).__init__(parent)

        self.okbutton = QtWidgets.QPushButton('Ok')
        self.okbutton.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        self.okbutton.clicked.connect(self.closedialog)

        workdir_label = QtWidgets.QLabel("WorkDir : ", self)
        self.workdir_line = QtWidgets.QLineEdit("./", self)
        self.workdir_line.move(20, 20)
        self.workdir_line.resize(280,40)
        workdir_button = QtWidgets.QPushButton("Browse")
        workdir_button.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        workdir_button.clicked.connect (self.workdir_browse)

        gridbin_label = QtWidgets.QLabel("Grid binary: ", self)
        self.gridbin_line = QtWidgets.QLineEdit("./grid", self)
        self.gridbin_line.move(20, 20)
        self.gridbin_line.resize(280,40)
        gridbin_button = QtWidgets.QPushButton("Browse")
        gridbin_button.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        gridbin_button.clicked.connect (self.gridbin_browse)

        fixpdbin_label = QtWidgets.QLabel("FixPdb binary: ", self)
        self.fixpdbin_line = QtWidgets.QLineEdit("./fixpdb", self)
        self.fixpdbin_line.move(20, 20)
        self.fixpdbin_line.resize(280,40)
        fixpdbin_button = QtWidgets.QPushButton("Browse")
        fixpdbin_button.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        fixpdbin_button.clicked.connect (self.fixpdbin_browse)

        apbsbin_label = QtWidgets.QLabel("APBS binary: ", self)
        self.apbsbin_line = QtWidgets.QLineEdit("/usr/bin/apbs", self)
        self.apbsbin_line.move(20, 20)
        self.apbsbin_line.resize(280,40)
        apbsbin_button = QtWidgets.QPushButton("Browse")
        apbsbin_button.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        apbsbin_button.clicked.connect (self.apbsbin_browse)

        obabelbin_label = QtWidgets.QLabel("OpenBabel binary: ", self)
        self.obabelbin_line = QtWidgets.QLineEdit("/usr/bin/obabel", self)
        self.obabelbin_line.move(20, 20)
        self.obabelbin_line.resize(280,40)
        obabelbin_button = QtWidgets.QPushButton("Browse")
        obabelbin_button.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        obabelbin_button.clicked.connect (self.obabelbin_browse)

        self.grid = QtWidgets.QGridLayout(self)

        self.grid.addWidget(workdir_label, 0, 0)
        self.grid.addWidget(self.workdir_line, 0, 1)
        self.grid.addWidget(workdir_button, 0, 2)

        self.grid.addWidget(gridbin_label, 1, 0)
        self.grid.addWidget(self.gridbin_line, 1, 1)
        self.grid.addWidget(gridbin_button, 1, 2)

        self.grid.addWidget(fixpdbin_label, 2, 0)
        self.grid.addWidget(self.fixpdbin_line, 2, 1)
        self.grid.addWidget(fixpdbin_button, 2, 2)

        self.grid.addWidget(apbsbin_label, 3, 0)
        self.grid.addWidget(self.apbsbin_line, 3, 1)
        self.grid.addWidget(apbsbin_button, 3, 2)

        self.grid.addWidget(obabelbin_label, 4, 0)
        self.grid.addWidget(self.obabelbin_line, 4, 1)
        self.grid.addWidget(obabelbin_button, 4, 2)

        self.grid.addWidget(self.okbutton, 5, 2)

    def closedialog(self):
        self.close()

    def gridbin_browse(self):

        path = QtWidgets.QFileDialog.getOpenFileName(self,
                "Open File", "./", "(*)")[0]

        self.gridbin_line.clear()       
        self.gridbin_line.insert (path)

    def fixpdbin_browse(self):

        path = QtWidgets.QFileDialog.getOpenFileName(self,
                "Open File", "./", "(*)")[0]

        self.fixpdbin_line.clear()       
        self.fixpdbin_line.insert (path)

    def apbsbin_browse(self):

        path = QtWidgets.QFileDialog.getOpenFileName(self,
                "Open File", "./", "(*)")[0]

        self.apbsbin_line.clear()       
        self.apbsbin_line.insert (path)

    def obabelbin_browse(self):

        path = QtWidgets.QFileDialog.getOpenFileName(self,
                "Open File", "./", "(*)")[0]

        self.obabelbin_line.clear()       
        self.obabelbin_line.insert (path)

    def workdir_browse(self):

        path = QtWidgets.QFileDialog.getExistingDirectory(self, \
            "Open Directory", "./", QtWidgets.QFileDialog.ShowDirsOnly | 
            QtWidgets.QFileDialog.DontResolveSymlinks)
                
        self.workdir_line.clear()
        self.workdir_line.insert (path)

