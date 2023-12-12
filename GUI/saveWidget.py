from PyQt5 import QtCore, QtGui, QtWidgets
from GUI.saveWidgetUI import Ui_saveForm
import datetime as dt
from PyQt5.QtCore import pyqtSignal, pyqtSlot

class saveW(QtWidgets.QWidget):
    saveSignal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.ui = Ui_saveForm()
        self.ui.setupUi(self)
        self.ui.saveButton.clicked.connect(self.ret_name)
        self.ui.dName.setText(str(dt.datetime.now().date()))
    @pyqtSlot()
    def ret_name(self):
        fName = self.ui.fName.text()
        dName = self.ui.dName.text()
        if len(fName) == 0:
            fName = 'UknownFile'
        if len(dName) == 0:
            dName = str(dt.datetime.now().date())
        self.saveSignal.emit("{}_{}.dat".format(fName,dName))
        return "{}_{}.dat".format(fName,dName)
        pass
