from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import sys, os, math
import numpy as np
import time

from HW.uController.uC import uC

class SingleShot(QObject()):
    finished = pyqtSignal(int, str, int, bool)
    progress = pyqtSignal(float)
    def __init__(self, uc:uC):
        super().__init__()
        self.Ts = 0
        self.Cth = 0
        self.Tz = 0
        self.Tq = 0
        self.Vq = 0
        self.cmdnr = 0
        self.UC = uc
        pass
    
    def set_args(self,Ts, Cth, Tz, Tq, Vq, cmdnr):
        self.Ts = Ts
        self.Cth = Cth
        self.Tz = Tz
        self.Tq = Tq
        self.Vq = Vq
        self.cmdnr = cmdnr
        pass
        
    def count(self):
        self.UC.countNi(self.Ts, self.Cth, self.Tz, self.Tq, self.Vq, self.cmdnr)
        step = self.Ts/100
        t = self.Ts
        while t > 0:
            time.sleep(step)
            self.progress.emit((self.Ts-t)/self.Ts)
            t = t - step
        Ni, statusas, ErrCode, code, crc_gautas, crc_apsk = self.UC.readNi()
        self.finished.emit(Ni, ErrCode, code, statusas)
        time.sleep(2)
        pass
