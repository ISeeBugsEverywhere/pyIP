from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import sys, os, math
import numpy as np
import time

from HW.uController.uC import uC

class SingleShot():
    progress = pyqtSignal(int, str, int, bool)
    def __init__(self, uc:uC):
        self.UC = uc
        pass
        
    def count(self, Ts, Cth, Tz, Tq, Vq, cmdnr):
        self.UC.countNi(Ts, Cth, Tz, Tq, Vq, cmdnr)
        time.sleep(1)
        Ni, statusas, ErrCode, code, crc_gautas, crc_apsk = self.UC.readNi()
        self.progress.emit(Ni, ErrCode, code, statusas)
        time.sleep(2)
        pass
