from PyQt5 import QtGui, QtCore, QtWidgets
import sys, os
from GUI.orielWidgetUI import Ui_orielForm
import time, math


WAVE_LABEL_TEXT = "Current wave [nm]: {}"

class OrielControlWidget(QtWidgets.QWidget):
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

    def _gui_(self):
        pass

    def sendCmd(self):
        cmd = self.ui.plainCmdBox.text()
        r = self.oriel.cmd(cmd)
        # self.ui.responsesField.appendPlainText("::CMD::\n{}".format(cmd))
        # self.ui.responsesField.appendPlainText(str(r))
        pass
    def go_fn(self):
        c_wave = float(self.oriel.wave())
        val =  self.ui.entryBox.value()
        unit = 'nm' # default
        n_wave = 0
        if val < 179:
            unit = 'ev'
            self.ui.evRadioBtn.setChecked(True)
            self.ui.nmRadioBtn.setChecked(False)
            n_wave = 1239.75/float(val)
        elif val > 180:
            unit = 'nm'
            self.ui.evRadioBtn.setChecked(False)
            self.ui.nmRadioBtn.setChecked(True)
            n_wave = val
        bts = self.oriel.gowave(val, unit)
        # self.ui.responsesField.appendPlainText(f"Bytes written: {bts}")
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
            # self.ui.responsesField.appendPlainText("Shutter is closed.")
            return "Shutter is closed."
        elif s.lower() == 'o':
            return "Shutter is opened."
            # self.ui.responsesField.appendPlainText("Shutter is opened.")
    def wave_fn(self):
        w = self.oriel.wave()
        self.ui.waveLabel.setText(WAVE_LABEL_TEXT.format(w))
        # self.ui.responsesField.appendPlainText(f"Current wave: {w}")
    pass
