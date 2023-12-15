import time

import numpy
import os
import sys
import serial

from HW.uController.crc import ComputeHash, CompareHash
from HW.uController.Functions import listIntegersToByteArray

from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

class uC():
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.port = serial.Serial() #configure and open it later
        pass

    def enable_port(self, port:str, ports_params:dict):
        self.port.port = port
        self.port.apply_settings(ports_params)
        try:
            self.port.open()
        except Exception as ex:
            print("::EX:{}::".format(str(ex)))
    # commands:

    def getIinValue(self, cmd_nr = 1):
        esc = 0x1b
        r = 0x72
        kiek = 2
        add = 0x82
        cmd_ = listIntegersToByteArray([esc, r, cmd_nr, kiek, add])
        crc = ComputeHash(cmd_)
        cmd = cmd_+crc
        cr, crcr, crc_r = None, None, None
        scaleStatusd = {0:'50 nA', 1:'500 nA'}
        try:
            self.port.write(cmd)
            time.sleep(1)
            r_ = self.port.read(24)
            cr, crcr, crc_r = CompareHash(r_)
            ErrCode = r_[-5]
            cmdNr = r_[-6]
            cmdRep = r_[-7]
            scaleStatus = int(r_[-8])
            return cr, crcr, crc_r, ErrCode, cmdNr, cmdRep, scaleStatus, scaleStatusd[scaleStatus]
        except Exception as ex:
            print('::EX:{}::'.format(str(ex)))







