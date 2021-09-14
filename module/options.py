from PyQt5 import QtGui, QtWidgets

class optiondialog_files(QtWidgets.QDialog):

    def __init__(self, parent=None):

        self.__mol2file1__ = ""

        super(optiondialog_files, self).__init__(parent)

        self.okbutton = QtWidgets.QPushButton('Ok')
        self.okbutton.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        self.okbutton.clicked.connect(self.closedialog)

        firstmol2file_label = QtWidgets.QLabel("First Multi-mol2 filename: ", self)
        self.firstmol2file_line = QtWidgets.QLineEdit("", self)
        self.firstmol2file_line.move(20, 20)
        self.firstmol2file_line.resize(280,40)
        firstmol2file_button = QtWidgets.QPushButton("Browse")
        firstmol2file_button.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        firstmol2file_button.clicked.connect (self.browsefirstmol2)

        secondmol2file_label = QtWidgets.QLabel("Second Multi-mol2 filename: ", self)
        self.secondmol2file_line = QtWidgets.QLineEdit("", self)
        self.secondmol2file_line.move(20, 20)
        self.secondmol2file_line.resize(280,40)
        secondmol2file_button = QtWidgets.QPushButton("Browse")
        secondmol2file_button.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        secondmol2file_button.clicked.connect (self.browsesecondmol2)

        firstweigfile_label = QtWidgets.QLabel("First Weight filename: ", self)
        self.firstweigfile_line = QtWidgets.QLineEdit("", self)
        self.firstweigfile_line.move(20, 20)
        self.firstweigfile_line.resize(280,40)
        firstweigfile_button = QtWidgets.QPushButton("Browse")
        firstweigfile_button.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        firstweigfile_button.clicked.connect (self.browsefirstweig)

        secondweigfile_label = QtWidgets.QLabel("Second Weight filename: ", self)
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

        self.grid.addWidget(secondmol2file_label, 1, 0)
        self.grid.addWidget(self.secondmol2file_line, 1, 1)
        self.grid.addWidget(secondmol2file_button, 1, 2)

        self.grid.addWidget(firstweigfile_label, 2, 0)
        self.grid.addWidget(self.firstweigfile_line, 2, 1)
        self.grid.addWidget(firstweigfile_button, 2, 2)

        self.grid.addWidget(secondweigfile_label, 3, 0)
        self.grid.addWidget(self.secondweigfile_line, 3, 1)
        self.grid.addWidget(secondweigfile_button, 3, 2)

        self.grid.addWidget(self.okbutton, 4, 2)

    def closedialog(self):
        self.close()

    def browsefirstmol2(self):

        mol2 = QtWidgets.QFileDialog.getOpenFileName(self,
                "Open File", "./", "mol2 (*.mol2)")[0]
                
        self.firstmol2file_line.insert (mol2)

    def browsesecondmol2(self):

        mol2 = QtWidgets.QFileDialog.getOpenFileName(self,
                "Open File", "./", "mol2 (*.mol2)")[0]
                
        self.secondmol2file_line.insert (mol2)
 
    def browsefirstweig(self):

        weig = QtWidgets.QFileDialog.getOpenFileName(self,
                "Open File", "./", "txt (*.txt)")[0]
                
        self.firstweigfile_line.insert (weig)

    def browsesecondweig(self):

        weig = QtWidgets.QFileDialog.getOpenFileName(self,
                "Open File", "./", "txt (*.txt)")[0]
                
        self.secondweigfile_line.insert (weig)
 
 
        
