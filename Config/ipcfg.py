import configparser as cfg
import os, sys

F = "Config/cfg.ini"

class CFG():
    def __init__(self):
        self.parser = cfg.ConfigParser()
        self.f = F
        self.__init__cfg()
        self.ini = ''
        self.get_ini()


    def __init__cfg(self):
        self.parser.read(self.f)

    def get_ini(self):
        f = open(self.f, mode='r')
        self.ini = f.read()
        f.close()

    def get_arduino(self, key:str):
        return self.parser['arduino'][key]
        pass

    def set_arduino(self, key, value):
        self.parser.set('arduino', key, value)

    def get_uc(self, key:str):
        return self.parser['uc'][key]
        pass

    def set_uc(self, key, value):
        self.parser.set('uc', key, value)


    def save_cfg(self):
        f = open(self.f, mode='w')
        self.parser.write(f, True)
        f.close()
