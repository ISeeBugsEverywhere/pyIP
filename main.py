from PyQt5 import QtCore, QtGui, QtWidgets
import sys, os
import numpy

from GUI.OrielWidget import OrielControlWidget
from GUI.mainIPWindowUI import Ui_IpMain
from GUI.saveWidget import saveW

class mainAppW(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_IpMain()
        self.ui.setupUi(self)
        self.ow = OrielControlWidget()
        self.saveW = saveW()
        self.__gui__()
        self.__signals__()
        pass

    def __gui__(self):
        l = self.ui.orielTab.layout()
        if l is None:
            l = QtWidgets.QVBoxLayout()
            l.setContentsMargins(0,0,0,0)
            # l.addWidget(self.ow, 0, 0, 1,1)
            l.addWidget(self.ow, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
            self.ui.orielTab.setLayout(l)
        else:
            l.addWidget(self.ow)
        l = self.ui.saveWidget.layout()
        if l is None:
            l = QtWidgets.QVBoxLayout()
            l.setContentsMargins(0, 0, 0, 0)
            # l.addWidget(self.ow, 0, 0, 1,1)
            l.addWidget(self.saveW, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
            self.ui.saveWidget.setLayout(l)
        # self.ui.orielTab.setFixedWidth(self.ow.width())
        self.ow.ui.goBtn.setIcon(QtGui.QIcon("GUI/Icons/play.png"))
        # self.ow.ui.connectBtn.setIcon(QtGui.QIcon("GUI/Icons/connect.png"))
        self.ow.ui.sendCmdBtn.setIcon(QtGui.QIcon("GUI/Icons/play.png"))
        self.ui.arduinoStatus.setPixmap(QtGui.QPixmap("GUI/Icons/memory.png"))
        self.ui.arduinoStatus.setScaledContents(True)
        self.ui.orielStatus.setPixmap(QtGui.QPixmap("GUI/Icons/oriel_q.png"))
        self.ui.orielStatus.setScaledContents(True)
        self.ui.ucStatus.setPixmap(QtGui.QPixmap("GUI/Icons/memory.png"))
        self.ui.ucStatus.setScaledContents(True)
        self.ui.mainStatus.setPixmap(QtGui.QPixmap("GUI/Icons/security-high.png"))
        self.ui.mainStatus.setScaledContents(True)
    def __signals__(self):
        pass

if __name__ == "__main__":
    app =  QtWidgets.QApplication(sys.argv)
    w = mainAppW()
    w.show()
    sys.exit(app.exec())