import sys, os
import pandas as pd
import numpy as np


class IzoEQ():
    def __init__(self, path:str):
        self.E = os.path.join(path, 'IzoE.txt')
        self.Q = os.path.join(path, 'IzoQ.txt')
        self.Edf = pd.read_csv(self.E)
        self.Qdf = pd.read_csv(self.Q)
    
    def GetEE(self, eV):
        t = -1
        r = -1
        if eV > 0:
            r = self.Edf[self.Edf['EV'] == eV]['C'].values[0]
        else:
            r = -1
        try:
            t = float(r)
        except Exception as ex:
            # print(ex)
            # print(eV)
            # print(r)
            t = -1
        return t
        pass
    
    def GetQQ(self, eV):
        t = -1
        r = -1
        if eV > 0:
            r = self.Qdf[self.Qdf['EV'] == eV]['C'].values[0]
        else:
            r = -1
        try:
            t = float(r)
        except Exception as ex:
            # print(ex)
            # print(eV)
            # print(r)
            t = -1
        return t
        pass
    
    def GetCorr(self, eV, Ni, t):
        '''
        eV, Ni
        return: EQQ, EEQ (IzoQ, IzoE); Per 1 sekundę!
        '''
        q = self.GetQQ(eV)
        e = self.GetEE(eV)
        EQQ = Ni
        EEQ = Ni
        if q > 0 and e > 0:
            EQQ = Ni/q
            EEQ = Ni/e
        # dalyba vykdoma čia, kad visais atvejais
        # būtų /s diemnsija
        return EQQ/t, EEQ/t