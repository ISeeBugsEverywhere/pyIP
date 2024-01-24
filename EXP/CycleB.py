from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import sys, os, math
import numpy as np
import time

from HW.uController.uC import uC
from HW.OrielHWCS260.OrielCS260USB import Oriel


class CycleB(QObject):
    progress = pyqtSignal(int, int, str) #Ni, %, eV
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
    
    
    def setEnd(self):
        self.end = True
        pass
    
    def run(self):
        '''
        runs cycle B:
        from eV to eV n times whole spectra
        '''
        p = 0
        points = ((self.maxE - self.minE)/self.step*self.r+self.bT*2)
        pct = int(p/points*100)
        # dark signal:
        self.ORIEL.closeShutter()
        time.sleep(1)
        for i in range(0, self.bT):
            statusas, bc, errMsg =  self.UC.countNi(self.Ts,self.Cth,self.Tz,self.Tq,self.Vq,self.cmdnr)
            if not statusas:
                self.error.emit(f'{errMsg}', f'Įrašytų baitų kiekis {bc}', 7)
                self.finished.emit(True)
                self.end = True
                break
            time.sleep(self.Ts*1.1)
            Ni, statusas, ErrCode, code, crc_gautas, crc_apsk, data = self.UC.readNi()
            if not statusas:
                self.error.emit(f'{ErrCode}', f'CRCs:{crc_gautas}/{crc_apsk}', code)
                self.finished.emit(True)
                self.end = True
                break
            p = p + 1
            pct = int(p/points*100)
            self.progress.emit(Ni, pct, 'Tamsa') #Ni, %, eV
            pass
        # end of first dark part
        ce = self.minE # einama energijų didėjimo kryptimi
        # shutter is opened:
        b = self.ORIEL.openShutter()
        time.sleep(1)
        for i in range(0,self.r):
            if self.end:
                    break
            while ce <= self.maxE and not self.end:                            
                # oriel eina į λ:
                λ = round(1239.75/ce, 3)
                n = self.ORIEL.gowave(λ)
                if n > 0:
                    # measure Ni:
                    statusas, bc, errMsg =  self.UC.countNi(self.Ts,self.Cth,self.Tz,self.Tq,self.Vq,self.cmdnr)
                    if not statusas:
                        self.error.emit(f'{errMsg}', f'Įrašytų baitų kiekis {bc}', 7)
                        self.finished.emit(True)
                        self.end = True
                        break
                    time.sleep(self.Ts*1.1)
                    Ni, statusas, ErrCode, code, crc_gautas, crc_apsk, data = self.UC.readNi()
                    if not statusas:
                        self.error.emit(f'{ErrCode}', f'CRCs:{crc_gautas}/{crc_apsk}', code)
                        self.finished.emit(True)
                        self.end = True
                        break
                    p = p + 1
                    pct = int(p/points*100)
                    self.progress.emit(Ni, pct, f'{ce:.3f}') #Ni, %, λ/eV
                    pass
                else:
                    self.error.emit('ORIEL - no bytes were written', '-9ERR', 9)
                    self.finished.emit(True)
                    self.end = True
                ce = ce + self.step
            pass
        # end of measurement cycle
        # dark signal, after main cycle:
        # dark signal:
        self.ORIEL.closeShutter()
        time.sleep(1)
        for i in range(0, self.bT):
            if self.end:
                    break
            statusas, bc, errMsg =  self.UC.countNi(self.Ts,self.Cth,self.Tz,self.Tq,self.Vq,self.cmdnr)
            if not statusas:
                self.error.emit(f'{errMsg}', f'Įrašytų baitų kiekis {bc}', 7)
                self.finished.emit(True)
                self.end = True
                break
            time.sleep(self.Ts*1.1)
            Ni, statusas, ErrCode, code, crc_gautas, crc_apsk, data = self.UC.readNi()
            if not statusas:
                self.error.emit(f'{ErrCode}', f'CRCs:{crc_gautas}/{crc_apsk}', code)
                self.finished.emit(True)
                self.end = True
                break
            p = p + 1
            pct = int(p/points*100)
            self.progress.emit(Ni, pct, 'Tamsa') #Ni, %, eV
            pass
        # end of dark
        # end of measurement cycle
        self.finished.emit(True)
        self.end = True
        pass