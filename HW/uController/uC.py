import numpy
import os
import sys
import serial

from HW.uController.crc import ComputeHash

from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

class uC():
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.port = serial.Serial() #configure and open it later
        pass

    def __enable_port(self, port:str, ports_params:dict):
        self.port.port = port
        self.port.apply_settings(ports_params)
        try:
            self.port.open()
        except Exception as ex:
            print("::EX:{}::".format(str(ex)))
    # commands:

    def readIin(self, cmd_nr:int):
        esc = 0x1b
        r = 0x72
        cmdNr = bytes(cmd_nr)
        kiek = 2
        address = 0x82
        cmd = [esc, r, cmdNr, kiek, address]
        Crc32 = bytes(ComputeHash(cmd))
        cmd32 = cmd + list(Crc32)
        if self.port.is_open:
            self.port.write(cmd32)




