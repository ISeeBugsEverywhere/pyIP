import numpy
import os
import sys
import serial


class uC():
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
