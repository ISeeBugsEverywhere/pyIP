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
        '''
        Init a CFG instance
        '''
        self.parser.read(self.f)

    def get_ini(self):
        '''
        reads ini file
        '''
        f = open(self.f, mode='r')
        self.ini = f.read()
        f.close()

    def get_arduino(self, key:str):
        '''Arduino part
        gets a value from key
        '''
        return self.parser['arduino'][key]
        pass

    def set_arduino(self, key, value):
        '''Arduino:
        updates a value'''
        self.parser.set('arduino', key, value)

    def get_uc(self, key:str):
        return self.parser['uc'][key]
        pass

    def set_uc(self, key, value):
        self.parser.set('uc', key, value)


    def save_cfg(self):
        '''Saves ini file'''
        f = open(self.f, mode='w')
        self.parser.write(f, True)
        f.close()

    def get_exp(self):
        '''

        :return: Ts,Cth,Tq,Tz,Vq
        '''
        Ts = self.parser['exp']['Ts']
        Cth = self.parser['exp']['Cth']
        Tq = int(self.parser['exp']['Tq'])
        Tz = int(self.parser['exp']['Tz'])
        Vq = int(self.parser['exp']['Vq'])
        return Ts,Cth,Tq,Tz,Vq

    def set_exp(self, Ts, Cth):
        self.parser.set('exp', 'Ts', Ts)
        self.parser.set('exp', 'Cth', Cth)
        self.save_cfg()
    
    def get_o2(self):
        '''

        :return: gas_value, p1, Topen, Tclose
        '''
        gas_value = self.parser['o2']['gas_value']
        p1 = self.parser['o2']['p1']
        Topen = self.parser['o2']['Topen']
        Tclose = self.parser['o2']['Tclose']
        return gas_value, p1, Topen, Tclose

    def set_o2(self, gv, p1, To, Tc):
        self.parser.set('o2', 'gas_value', gv)
        self.parser.set('o2', 'p1', p1)
        self.parser.set('o2', 'Topen', To)
        self.parser.set('o2', 'Tclose', Tc)
        self.save_cfg()
