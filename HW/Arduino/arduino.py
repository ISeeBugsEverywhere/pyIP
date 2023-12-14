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
        if self.port.is_open:
            while not self.stop:
                size= self.port.in_waiting
                if size:
                    data = self.port.read(size)
                    r = data.decode('utf-8')
                    self.progress.emit(r)
        else:
            self.progress.emit("::PORT IS CLOSED OR IN USE::")

    def end(self, arg):
        self.stop = arg






