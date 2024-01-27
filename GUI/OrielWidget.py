from PyQt5 import QtGui, QtCore, QtWidgets
import sys, os
from GUI.orielWidgetUI import Ui_orielForm
import time, math
from PyQt5.QtCore import pyqtSlot, pyqtSignal


WAVE_LABEL_TEXT = "λ [nm]: {}"

class OrielControlWidget(QtWidgets.QWidget):
    qtSignal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.ui = Ui_orielForm()
        self.ui.setupUi(self)
        self.signals()
        self.oriel = None
        self._gui_()

    def setOriel(self, oriel):
        self.oriel = oriel

    def signals(self):
        self.ui.goBtn.clicked.connect(self.go_fn)
        self.ui.shutterToggleBtn.clicked.connect(self.toggle_fn)
        self.ui.shutterCheckBtn.clicked.connect(self.check_fn)
        self.ui.waveBtn.clicked.connect(self.wave_fn)
        self.ui.sendCmdBtn.clicked.connect(self.sendCmd)
        self.ui.entryBox.editingFinished.connect(self.checkFn)

    def _gui_(self):
        pass
    
    def checkFn(self):
        val = self.ui.entryBox.value()
        if val > 6.5 and val < 198:
            self.ui.entryBox.setValue(6.25)
            self.ui.evRadioBtn.setChecked(True)
        elif val > 1000:
            self.ui.entryBox.setValue(1000)
            self.ui.nmRadioBtn.setChecked(True)

    def sendCmd(self):
        cmd = self.ui.plainCmdBox.text()
        r = self.oriel.cmd(cmd)
        self.qtSignal.emit("CMD:{}, RES: {}".format(cmd, r))
        pass
    
    def go_fn(self):
        c_wave = float(self.oriel.wave())
        val =  self.ui.entryBox.value()
        unit = 'nm' # default
        n_wave = 0
        if val < 7:
            unit = 'ev'
            self.ui.evRadioBtn.setChecked(True)
            self.ui.nmRadioBtn.setChecked(False)
            n_wave = 1239.75/float(val)
        elif val >= 198:
            unit = 'nm'
            self.ui.evRadioBtn.setChecked(False)
            self.ui.nmRadioBtn.setChecked(True)
            n_wave = val
        bts = self.oriel.gowave(val, unit)
        self.qtSignal.emit("Bytes written {}".format(bts))
        #     delay?
        time.sleep(math.floor(abs(c_wave-n_wave))/10.0*0.125)
        cw = self.oriel.wave()
        self.ui.waveLabel.setText(WAVE_LABEL_TEXT.format(cw))

    def toggle_fn(self):
        s = self.oriel.shutter()
        if s.lower() == 'c':
            self.oriel.openShutter()
            self.ui.shutterStatusLabel.setText("OPENED")
        elif s.lower() == 'o':
            self.oriel.closeShutter()
            self.ui.shutterStatusLabel.setText("CLOSED")
    def check_fn(self):
        s = self.oriel.shutter()
        if s.lower() == 'c':
            self.qtSignal.emit('SHUTTER CLOSED.')
            self.ui.shutterStatusLabel.setText("CLOSED")
        elif s.lower() == 'o':
            self.qtSignal.emit('SHUTTER OPENED.')
            self.ui.shutterStatusLabel.setText("OPENED")


    def wave_fn(self):
        w = self.oriel.wave()
        self.ui.waveLabel.setText(WAVE_LABEL_TEXT.format(w))

    pass
