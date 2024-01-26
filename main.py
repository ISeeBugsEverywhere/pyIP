from PyQt5 import QtCore, QtGui, QtWidgets
import sys, os
import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QObject

from GUI.OrielWidget import OrielControlWidget, WAVE_LABEL_TEXT
from GUI.mainIPWindowUI import Ui_IpMain
from GUI.saveWidget import saveW

from Config.ipcfg import CFG, F
from GUI.getFunctions import *

from HW.Arduino.arduino import ArduinoWatcher
from HW.OrielHWCS260.OrielCS260USB import Oriel
from HW.uController.uC import uC

import subprocess
import glob

import pyqtgraph as pq

from EXP.Single import SingleShot #1nam matavimui
from EXP.CycleA import CycleA #cycleA
from EXP.CycleB import CycleB #cycleB
from CALIBR.IzoQE import IzoEQ

MSG = f"{'E[eV]': ^10}{'Ni[c]': ^10}{'EQQ/s': ^10}{'EEQ/s': ^10}{'O2[%]': ^10}{'U[V]': ^10}\n"+'='*60


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
        self.ExpThread = QThread(parent=self)
        self.ExpObject = None
        V = self.cfg.parser['oriel']['VENDOR_ID']
        P = self.cfg.parser['oriel']['PRODUCT_ID']
        self.oriel = Oriel(int(V, 16), int(P, 16))
        var = self.cfg.parser['uc']['model']
        self.uC = uC(var)
        self.debug = False
        self.QQ = IzoEQ('CALIBR')
        self.plotData = {}
        self.eVs = []
        self.Nis = []


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
        self.ui.actionDebug.setIcon(QtGui.QIcon('GUI/Icons/configure.png'))
        self.ui.actionU_daryti.setIcon(QtGui.QIcon('GUI/Icons/quit.png'))        
        self.ui.experimentOutputEdit.setPlainText(MSG)
        self.ui.plotWidget.setBackground('#FFFFFF')
        self.ui.plotWidget.getPlotItem().getAxis('bottom').setLabel(text='Energija', units='eV')
        self.ui.plotWidget.getPlotItem().getAxis('left').setLabel(text='Ni[c]')
        mpen = QtGui.QPen(QtGui.QColor('black'))
        mpen.setWidth(2)
        self.ui.plotWidget.getPlotItem().getAxis('left').setTextPen(mpen)
        self.ui.plotWidget.getPlotItem().getAxis('bottom').setTextPen(mpen)
        pass



    def __signals__(self):
        self.ui.connectBtn.clicked.connect(self.cnt_fn)
        self.ow.qtSignal.connect(self.responseField)
        self.saveW.saveSignal.connect(self.save_data)
        self.ui.setVoltageBtn.clicked.connect(self.set_voltage_fn)
        self.ui.plus50VBtn.clicked.connect(self.p50Vfn)
        self.ui.minus50VBtn.clicked.connect(self.m50Vfn)
        self.ui.set2kVBtn.clicked.connect(self.set2kVfn)
        self.ui.actionU_daryti.triggered.connect(self.exit_fn)
        self.ui.renewArduinoBtn.clicked.connect(self.renewArduinoParams)
        self.ui.startStopArduino.clicked.connect(self.startStopArduino)
        self.ui.shutterGassBtn.clicked.connect(self.shutterGasFn)
        self.ui.saveParamsBtn.clicked.connect(self.saveParamsFn)
        self.ui.reloadParamsBtn.clicked.connect(self.reloadParamsFn)
        self.ui.actionDebug.triggered.connect(self.dbgfn)
        # valdiklis:
        self.ui.oneBtn.clicked.connect(self.oneMeasurement) #singleshot'as
        # Cycles (A/B/C)
        self.ui.doBtn.clicked.connect(self.mCycleStart)
        
        pass
    
    def mCycleStart(self):
        r = False
        if 'matuot' in self.ui.doBtn.text().lower():
            r = True
            self.ui.doBtn.setText('STOP')
        elif 'sto' in self.ui.doBtn.text().lower():
            r = False
            self.ExpObject.setEnd()
            self.ui.doBtn.setText('Matuoti')
            self.ui.expProgressBar.setValue(0)
            self.ExpThread.quit()
        if 'A' in self.ui.expStyleComboBox.currentText() and r:
            # A:            
            Ts = self.ui.TsBox.value()
            Cth = int(self.ui.cthBox.value())
            maxE = self.ui.stopEVBox.value()
            minE = self.ui.startEVBox.value()
            step = self.ui.stepEVBox.value()
            repeats = self.ui.repeatBox.value()
            backgroundTimes = self.ui.darkCounterBox.value()
            self.ExpThread = QThread(parent=self)
            self.ExpObject = CycleA(self.uC, self.oriel)
            self.ExpObject.set_args(Ts, Cth, self.Tz, self.Tq, self.Vq, 1, minE, maxE, step, repeats, backgroundTimes)
            self.ExpObject.moveToThread(self.ExpThread)
            self.ExpThread.started.connect(self.ExpObject.run)
            self.ExpObject.progress.connect(self.cycleProgress)
            self.ExpObject.finished.connect(self.cycleFinished)
            self.ExpObject.error.connect(self.cycleError)
            self.ExpThread.start()
            pass
        elif 'B' in self.ui.expStyleComboBox.currentText() and r:
            # :B
            # B:            
            Ts = self.ui.TsBox.value()
            Cth = int(self.ui.cthBox.value())
            maxE = self.ui.stopEVBox.value()
            minE = self.ui.startEVBox.value()
            step = self.ui.stepEVBox.value()
            repeats = self.ui.repeatBox.value()
            backgroundTimes = self.ui.darkCounterBox.value()
            self.ExpThread = QThread(parent=self)
            self.ExpObject = CycleB(self.uC, self.oriel)
            self.ExpObject.set_args(Ts, Cth, self.Tz, self.Tq, self.Vq, 1, minE, maxE, step, repeats, backgroundTimes)
            self.ExpObject.moveToThread(self.ExpThread)
            self.ExpThread.started.connect(self.ExpObject.run)
            self.ExpObject.progress.connect(self.cycleProgress)
            self.ExpObject.finished.connect(self.cycleFinished)
            self.ExpObject.error.connect(self.cycleError)
            self.ExpThread.start()
            pass
        elif 'C' in self.ui.expStyleComboBox.currentText() and r:
            # C
            self.check('C dalis nerealizuota', ignore=True)
            pass
        pass
    
    def cycleProgress(self, Ni, p, eV):
        # progress = pyqtSignal(int, int, str) #Ni, %, eV (int, int, str!!!)
        # finished = pyqtSignal(bool)
        # error = pyqtSignal(str, str, int) #Exception, ErrCode, errcode
        if eV.lower() == 'tamsa':
            eV = -1
        else:
            cpl = round(1239.75/float(eV), 3)
            self.ow.ui.waveLabel.setText(WAVE_LABEL_TEXT.format(cpl))
        Ts = self.ui.TsBox.value()
        EQQ, EEQ = self.QQ.GetCorr(round(float(eV), 3), Ni, Ts)
        if eV == -1:
            eV = 'Tamsa'
        o2 = self.ui.lcdO2.value()
        Uvaldiklio = self.ui.uBox.value()
        msg = f'{eV: ^10}{Ni: ^10.0f}{EQQ: ^10.2f}{EEQ: ^10.2f}{o2: ^10.2f}{Uvaldiklio: ^10}'
        self.ui.experimentOutputEdit.appendPlainText(msg)
        self.plotPoints(eV, Ni)
        self.ui.expProgressBar.setValue(p)
        pass
    
    def cycleFinished(self, b):
        # progress = pyqtSignal(int, int, str) #Ni, %, λ
        # finished = pyqtSignal(bool)
        # error = pyqtSignal(str, str, int) #Exception, ErrCode, errcode
        self.ExpObject.setEnd()
        self.ui.doBtn.setText('Matuoti')
        self.ExpThread.quit()
        self.ui.expProgressBar.setValue(0)
        pass
    
    def cycleError(self, ex, ErrMsg, errCode):
        self.check(ex, ErrMsg, errCode, ignore=True)
        self.ExpThread.quit()
        pass
    
    def oneMeasurement(self):
        self.check('one Measurement')
        Ts = self.ui.TsBox.value()
        Cth = self.ui.cthBox.value()
        self.check("::CTH", Cth)
        self.ExpObject = SingleShot(self.uC)
        self.ExpObject.set_args(Ts, Cth, self.Tz, self.Tq, self.Vq, 1)
        self.ExpObject.moveToThread(self.ExpThread)
        self.ExpThread.started.connect(self.ExpObject.count)
        self.ExpObject.progress.connect(self.expProgressBarFn)
        self.ExpObject.finished.connect(self.expSingleFinished)
        self.ExpThread.start()
    
    def expProgressBarFn(self, p:float):
        self.ui.expProgressBar.setValue(int(p*100))
        pass
    
    def expSingleFinished(self, Ni, ErrCode, code, statusas):
        self.check(Ni, ErrCode, code, statusas)
        t = self.ow.ui.waveLabel.text()
        i = t.find(':')
        λ = -1.0
        eV = -1.0
        Uvaldiklio = self.ui.uBox.value()
        try:
            λ = float(t[i+1:]) #neturi įeiti :
        except Exception as ex:
            λ = -1.0
            self.check('λ nenustatytas')
        if λ > 0:
            eV = round(1239.75/λ, 3)
        Ts = self.ui.TsBox.value()
        EQQ, EEQ = self.QQ.GetCorr(eV, Ni, Ts)
        o2 = self.ui.lcdO2.value()
        data_str = f'{eV: ^10}{Ni: ^10.0f}{EQQ: ^10.2f}{EEQ: ^10.2f}{o2: ^10.2f}{Uvaldiklio: ^10}'
        self.ui.experimentOutputEdit.appendPlainText(data_str)
        self.check(f'{λ:.2f} | {Ni} | {ErrCode}')
        # QThread must be destroyied:
        # self.ExpThread = QThread(parent=self)
        self.ui.expProgressBar.setValue(0)
        self.ExpThread.quit()
        # self.ExpThread.deleteLater()
        pass
        
        # self.uC.countNi(Ts,Cth, self.Tz, self.Tq, self.Vq, 1)
    
    def dbgfn(self):
        if self.ui.actionDebug.isChecked():
            self.ui.responsesField.append("::DEBUG ENABLED::")
            self.debug = True
        else:
            self.ui.responsesField.append("::DEBUG DISABLED::")
            self.debug = False
    
    def check(self, *msg, ignore=False):
        if not self.debug and ignore:            
            n = []
            for i in msg:
                n.append(str(i))
            m = ' '.join(n)
            self.ui.responsesField.append(m)
        elif self.debug:
            n = []
            for i in msg:
                n.append(str(i))
            m = ' '.join(n)
            self.ui.responsesField.append(m)
    
    def reloadParamsFn(self):
        # self.cfg = None
        # time.sleep(1)
        self.cfg = CFG()
        pass
    
    def saveParamsFn(self):
        params = self.ui.parametersEdit.toPlainText()
        f = open(F, mode='w')
        f.write(params)
        f.close()
        pass
    
    def renewArduinoParams(self):
        '''Updates arduino with new parameters'''
        cmd_o2 = 'o2'
        o2_lvl = int(self.ui.gasValueBox.value()*100) #D4
        threshold = self.ui.gasP1Box.value() #D2
        open_ = self.ui.s1Box.value() #D2
        delay_ = self.ui.delayS1Box.value() #D2
        cmd_o = f"{cmd_o2}{o2_lvl:04.0f}{threshold:02.0f}t{open_:02.0f}{delay_:02.0f}!"
        self.ArduinoWatch.write(cmd=cmd_o)
        # print(cmd_o)
        pass
    
    def startStopArduino(self):
        '''Stops/Starts Arduino'''
        if self.ui.startStopArduino.text() == 'Start':
            self.ArduinoWatch.started()
            self.ui.startStopArduino.setText('Stop')
        elif self.ui.startStopArduino.text() == 'Stop':
            self.ArduinoWatch.stoped()
            self.ui.startStopArduino.setText('Start')
        pass
    
    def shutterGasFn(self):
        '''Checks gas shutter state via Arduino'''
        self.ArduinoWatch.write('t')
        pass

    def exit_fn(self):
        sys.exit(0)

    def p50Vfn(self):
        v = self.ui.uBox.value()
        v =  v + 50
        self.ui.uBox.setValue(v)
        self.set_voltage_fn()
        pass

    def m50Vfn(self):
        v = self.ui.uBox.value()
        v = v - 50
        self.ui.uBox.setValue(v)
        self.set_voltage_fn()
        pass

    def set2kVfn(self):
        self.ui.uBox.setValue(2000)
        self.set_voltage_fn()
        pass

    def set_voltage_fn(self):
        self.ui.voltageStatusLabel.setPixmap(QtGui.QPixmap('GUI/Icons/voltageStatusQ.png'))
        kV =  round(self.ui.uBox.value() / 1000.0, 4)
        crc_status, crcr, crc_r, ErrCode, cmdNr, cmdRep, crc_v, cmd_crc = self.uC.setVoltage(kV, 1, 2 )
        self.check(crc_status, crcr, crc_r, ErrCode, cmdNr, cmdRep, crc_v, cmd_crc)
        if crc_status:
            self.ui.voltageStatusLabel.setPixmap(QtGui.QPixmap('GUI/Icons/voltageStatusOK.png'))
        else:
            self.ui.voltageStatusLabel.setPixmap(QtGui.QPixmap('GUI/Icons/voltageStatusFF.png'))

    def save_data(self, fname:str):
        data = self.ui.experimentOutputEdit.toPlainText()
        p = self.cfg.parser['path']['path']
        fp = os.path.join(p, fname)
        f_ = open(fp, mode='w')
        f_.write(data)
        f_.close()
        self.ui.experimentOutputEdit.setPlainText(MSG)
        self.plotData = {}
        self.eVs = []
        self.Nis = []
        self.ui.plotWidget.clear()


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
        V = self.cfg.parser['oriel']['VENDOR_ID']
        P = self.cfg.parser['oriel']['PRODUCT_ID']
        self.oriel = Oriel(int(V, 16), int(P, 16))
        var = self.cfg.parser['uc']['model']
        self.uC = uC(var)
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
        o2, t, o22, ch4, status_msg, code, dht, rem, fs = self.ArduinoParser.analyzeArd(s)
        if code == 2:
            self.ui.responsesField.append(rem)
            if 'closed' in rem.lower():
                self.ui.shutterSttausLabel.setText('UŽD.')
            if 'opened' in rem.lower():
                self.ui.shutterSttausLabel.setText('ATID.')
        elif code == 0:
            self.ui.lcdO2.display(o2.replace(':',''))
            self.ui.lcdT.display(t)
        elif code == 1:
            self.ui.lcdH.display(dht)
        else:
            pass

    def responseField(self, s:str):
        self.ui.responsesField.append(s)
        pass
    
    def plotPoints(self, eV, Ni):
        ev = -1.0
        if eV != 'Tamsa':
            ev = float(eV)
            self.plotData[ev] = Ni
            self.eVs.append(ev)
            self.Nis.append(Ni)
        self.ui.plotWidget.clear()
        scItem = pq.ScatterPlotItem()
        scItem.setSize(16)
        mPen = QtGui.QPen()
        mPen.setColor(QtGui.QColor('#06470c'))
        mPen.setWidth(3)
        scItem.setPen(mPen)
        mBrush = QtGui.QBrush()
        mBrush.setColor(QtGui.QColor('#06470c'))
        scItem.setData(x=self.eVs, y=self.Nis)
        self.ui.plotWidget.addItem(scItem)
        pass


if __name__ == "__main__":
    app =  QtWidgets.QApplication(sys.argv)
    w = mainAppW()
    w.show()
    sys.exit(app.exec())