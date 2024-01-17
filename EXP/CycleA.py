from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import sys, os, math
import numpy as np
import time

from HW.uController.uC import uC
from HW.OrielHWCS260.OrielCS260USB import Oriel


class CycleA(QObject):
    progress = pyqtSignal(int, int, str) #Ni, %, λ
    finished = pyqtSignal(bool)
    error = pyqtSignal(str, str, int) #Exception, ErrCode, errcode
    def __init__(self, uc:uC, oriel:Oriel):
        super().__init__()
        self.Ts = 0
        self.Cth = 0
        self.Tz = 0
        self.Tq = 0
        self.Vq = 0
        self.cmdnr = 0
        self.minE = 0
        self.maxE = 0
        self.step = 0
        self.r = 0 #kiek kartų vieną tašką matuoti
        self.bT = 0 #kiek kartų matuoti foną prieš VISĄ šviesinį spektrą
        self.UC = uc
        self.ORIEL = oriel
        self.end = False
        pass
    
    def set_args(self,Ts, Cth, Tz, Tq, Vq, cmdnr, minE, maxE, step, repeats, backgroundTimes):
        self.Ts = Ts
        self.Cth = Cth
        self.Tz = Tz
        self.Tq = Tq
        self.Vq = Vq
        self.cmdnr = cmdnr
        self.minE = minE
        self.maxE = maxE
        self.step = step
        self.r = repeats
        self.bT = backgroundTimes
        pass
    
    def run(self):
        '''
        runs cycle A:
        from to n times each point
        '''
        # dark signal:
        self.ORIEL.closeShutter()
        time.sleep(2)
        for i in range(0, self.bT):
            statusas, bc, errMsg =  self.UC.countNi(self.Ts,self.Cth,self.Tz,self.Tq,self.Vq,self.cmdnr)
            if not statusas:
                self.error.emit(f'{errMsg}', f'Įrašytų baitų kiekis {bc}', 7)
                self.finished.emit(True)
                self.end = True
                break
            time.sleep(self.Ts*1.1)
            Ni, statusas, ErrCode, code, crc_gautas, crc_apsk = self.UC.readNi()
            if not statusas:
                self.error.emit(f'{ErrCode}', f'CRCs:{crc_gautas}/{crc_apsk}', code)
                self.finished.emit(True)
                self.end = True
                break
            self.progress.emit(Ni, 10, 'tamsa') #Ni, %, λ
            pass
        ce = self.minE
        # shutter is opened:
        b = self.ORIEL.openShutter()
        time.sleep(2)
        while ce <= self.maxE and not self.end:
            for i in range(0,self.r):                
                pass
            ce = ce + self.step
            pass
        self.finished.emit(True)
        self.end = True
        pass