from PyQt5 import QtGui, QtWidgets

class optiondialog_files(QtWidgets.QDialog):

    def __init__(self, parent=None):

        self.__mol2file1__ = ""

        super(optiondialog_files, self).__init__(parent)

        self.okbutton = QtWidgets.QPushButton('Ok')
        self.okbutton.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        self.okbutton.clicked.connect(self.closedialog)

        firstmol2file_label = QtWidgets.QLabel("First Multi-mol2 filename: ", self)
        self.firstmol2file_line = QtWidgets.QLineEdit(str(self.__mol2file1__), self)
        self.firstmol2file_line.move(20, 20)
        self.firstmol2file_line.resize(280,40)
        firstmol2file_button = QtWidgets.QPushButton("Browse")
        firstmol2file_button.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        firstmol2file_button.clicked.connect (self.browsefirstmol2)

        self.grid = QtWidgets.QGridLayout(self)

        self.grid.addWidget(firstmol2file_label)
        self.grid.addWidget(self.firstmol2file_line)
        self.grid.addWidget(firstmol2file_button)

        self.grid.addWidget(self.okbutton)

    def closedialog(self):
        self.close()

    def browsefirstmol2(self):

        self.__firstmol2__ = QtWidgets.QFileDialog.getOpenFileName(self,
                "Open File", "./", "mol2 (*.mol2)")[0]
