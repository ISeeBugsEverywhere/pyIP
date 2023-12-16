from PyQt5 import QtCore, QtGui, QtWidgets
import sys, os
import numpy
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QObject

from GUI.OrielWidget import OrielControlWidget
from GUI.mainIPWindowUI import Ui_IpMain
from GUI.saveWidget import saveW

from Config.ipcfg import CFG
from GUI.getFunctions import *

from HW.Arduino.arduino import ArduinoWatcher
from HW.OrielHWCS260.OrielCS260USB import Oriel
from HW.uController.uC import uC

import subprocess
import glob



class mainAppW(QtWidgets.QMainWindow):
    cfg = CFG()
    def __init__(self):
        super().__init__()
        self.ArduinoWatch = None
        self.ui = Ui_IpMain()
        self.ui.setupUi(self)
        self.ow = OrielControlWidget()
        self.saveW = saveW()
        self.Tq = 0
        self.Tz = 0
        self.Vq = 0
        self.usbDevices = {}
        self.__gui__()
        self.__signals__()
        self.ArdQThread = QThread()
        self.ArduinoParser = ArdParser()
        self.oriel = Oriel()
        self.uC = uC()


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
        self.ui.arduinoStatus.setPixmap(QtGui.QPixmap("GUI/Icons/Quest.png"))
        self.ui.arduinoStatus.setScaledContents(True)
        self.ui.orielStatus.setPixmap(QtGui.QPixmap("GUI/Icons/oriel_q.png"))
        self.ui.orielStatus.setScaledContents(True)
        self.ui.ucStatus.setPixmap(QtGui.QPixmap("GUI/Icons/Quest.png"))
        self.ui.ucStatus.setScaledContents(True)
        self.ui.mainStatus.setPixmap(QtGui.QPixmap("GUI/Icons/Run.PNG"))
        self.ui.mainStatus.setScaledContents(True)
        self.ui.parametersEdit.setPlainText(self.cfg.ini)
        p_ = get_serial_ports()
        self.usbDevices = p_
        self.ui.arduinoSerialBox.addItems(p_.keys())
        self.ui.ucSerialBox.addItems(p_.keys())
        self.ui.connectBtn.setIcon(QtGui.QIcon('GUI/Icons/connect.png'))
        # parametrai:
        # exp:
        Ts,Cth,self.Tq,self.Tz,self.Vq = self.cfg.get_exp()
        self.ui.TsBox.setValue(int(Ts))
        self.ui.cthBox.setValue(float(Cth))
        # o2:
        gas_value, p1, Topen, Tclose = self.cfg.get_o2()
        self.ui.gasValueBox.setValue(float(gas_value))
        self.ui.gasP1Box.setValue(int(p1))
        self.ui.s1Box.setValue(int(Topen))
        self.ui.delayS1Box.setValue(int(Tclose))
        # portai:
        ardP = self.cfg.get_arduino('port')
        if ardP:
            idx = self.ui.arduinoSerialBox.findText(ardP)
            if idx != -1:
                self.ui.arduinoSerialBox.setCurrentIndex(idx)
        ucP = self.cfg.get_uc('port')
        if ucP:
            idx = self.ui.ucSerialBox.findText(ucP)
            if idx != -1:
                self.ui.ucSerialBox.setCurrentIndex(idx)
        pass



    def __signals__(self):
        self.ui.connectBtn.clicked.connect(self.cnt_fn)
        self.ow.qtSignal.connect(self.responseField)

    def cnt_fn(self):
        if self.ui.connectBtn.text() == 'Prisijungti':
            self.connect_fn()
            self.ui.connectBtn.setText('Atsijungti')
        elif self.ui.connectBtn.text() == 'Atsijungti':
            self.dis_fn()
        pass

    def dis_fn(self):
        self.ArduinoWatch.end(True)
        self.ArdQThread.quit()
        self.ArdQThread.wait()
        self.oriel.remove()
        self.oriel = Oriel()
        self.ui.connectBtn.setText('Prisijungti')
    def connect_fn(self):
        # arduino part:
        prms = get_port_param_dct('arduino', self.cfg)
        ard_p = self.ui.arduinoSerialBox.currentText()
        self.ArduinoWatch = ArduinoWatcher(self.usbDevices[ard_p], prms)
        self.ArduinoWatch.moveToThread(self.ArdQThread)
        self.ArdQThread.started.connect(self.ArduinoWatch.watch)
        self.ArduinoWatch.progress.connect(self.reportArduinoData)
        self.ArdQThread.start()
        # save port:
        self.cfg.set_arduino('port', ard_p)
        self.cfg.save_cfg()
        self.ui.arduinoStatus.setPixmap(QtGui.QPixmap('GUI/Icons/ARDUINO.png'))
        self.ui.arduinoStatus.setScaledContents(True)
        # oriel
        r = self.oriel.setup()
        if r == 0:
            self.ow.setOriel(self.oriel)
            self.ui.orielStatus.setPixmap(QtGui.QPixmap('GUI/Icons/oriel_ok.png'))
            self.ui.orielStatus.setScaledContents(True)
        else:
            self.ui.orielStatus.setPixmap(QtGui.QPixmap('GUI/Icons/oriel_no.png'))
            self.ui.orielStatus.setScaledContents(True)
        # Valdiklis:
        up = get_port_param_dct('uc', self.cfg)
        up_port = self.ui.ucSerialBox.currentText()
        self.uC.enable_port(self.usbDevices[up_port], up)
        r = self.uC.getIinValue(42)
        if r is not None:
            cr, crcr, crc_r, ErrCode, cmdNr, cmdRep, scaleStatus, status_msg = r
            self.ui.responsesField.append(f"{status_msg}, {ErrCode}, {crcr}, μK, {crc_r}, m.crc")
            self.cfg.set_uc('port', up_port)
            self.cfg.save_cfg()
            if cr:
                self.ui.ucStatus.setPixmap(QtGui.QPixmap('GUI/Icons/micro.png'))
                self.ui.ucStatus.setScaledContents(True)
            else:
                self.ui.ucStatus.setPixmap(QtGui.QPixmap('GUI/Icons/NOMICRO.png'))
                self.ui.ucStatus.setScaledContents(True)
        pass

    def reportArduinoData(self, s:str):
        o2, t, o22, ch4, status_msg, code, dht, rem = self.ArduinoParser.analyzeArd(s)
        if code == 2:
            self.ui.responsesField.append(rem)
        if code == 0:
            self.ui.lcdO2.display(o2)
            self.ui.lcdT.display(t)
        if code == 1:
            self.ui.lcdH.display(dht)

    def responseField(self, s:str):
        self.ui.responsesField.append(s)


if __name__ == "__main__":
    app =  QtWidgets.QApplication(sys.argv)
    w = mainAppW()
    w.show()
    sys.exit(app.exec())