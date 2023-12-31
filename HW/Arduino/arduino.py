import serial
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QThread
import math, sys, os, time

class ArduinoWatcher(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)
    def __init__(self, port:str, port_params:dict):
        super().__init__()
        self.port = serial.Serial()
        self.p_ = port
        self.settings = port_params
        self.initSerial()
        self.stop = False

    def initSerial(self):
        self.port.apply_settings(self.settings)
        self.port.port = self.p_
        self.port.open()

    def watch(self):
        if self.port.is_open and not self.stop:
            while not self.stop:
                size= self.port.in_waiting
                if size:
                    data = self.port.read(size)
                    r = data.decode('utf-8')
                    self.progress.emit(r)
        else:
            self.progress.emit("::PORT IS CLOSED OR IN USE::")
            # self.port.close()

    def end(self, arg):
        print('::STOP ARD::')
        self.stop = arg

    def write(self, cmd:str):
        if self.port.is_open:
            self.port.write(bytes(cmd))


    def get(self):
        r_ = 'NULL'
        if self.port.is_open:
            s = self.port.in_waiting
            r = self.port.read(s)
            r_ = r.decode('utf-8')
        return  r_








