import struct
import time

import numpy
import os
import sys
import serial

from HW.uController.crc import ComputeHash, CompareHash
from HW.uController.Functions import listIntegersToByteArray

from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot

class uC():
    crcErr = {0:"Komada O.K.",1:"CRC32 blogas",2:"Bloga komanda",3:"Blogas parametras",4:"τ>0.1s (timeout)",5:"U per maža",6:"U per didelė"}
    # progress = pyqtSignal(str)
    # finished = pyqtSignal(str)
    def __init__(self, A:str):
        super().__init__()
        self.port = serial.Serial() #configure and open it later
        self.model = A #A, B; strings
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
            ErrCode = self.crcErr[r_[-5]]
            cmdNr = r_[-6]
            cmdRep = r_[-7]
            scaleStatus = int(r_[-8])
            return cr, crcr, crc_r, ErrCode, cmdNr, cmdRep, scaleStatus, scaleStatusd[scaleStatus]
        except Exception as ex:
            print('::EX:{}::'.format(str(ex)))


    def setVoltage(self, kV, cmd_nr:int, kiekData):
        '''
        Rašymui/skaitymui (iki 0x0f):
        1:0	42Vset35:  nustatyta HV išėjimo įtampa. 0 atitinka 4.2kV, 0xfff atitinka 2.0 kV.
        3:2	Kp:  proporcingumo koeficientas dėl išėjimo PWM apskaičiavimo: PWM= Kp* impulsų_kiekis_pe_1_s / 0x1000.
        4	Vq: gesinimo įtampa 0-0xff (0-100V)
        konversija:
        x = 4095*(4,2kV-U kV)/2,2kV;
        Rašyti atmintį.
        Esc  w nr Add  Kiek  Duomenys CRC32

        Add atminties adresas (baitas) 0...0x0f
        Kiek įrašomų baitų kiekis 1...0x10
        Duomenys – įrašomi duomenys, jų kiekis turi būti Kiek.
        :return:
        '''
        esc = 0x1b
        w = 0x77
        nr = cmd_nr
        add = 0x70
        kiek = kiekData+1 #?? kodėl +1?
        f42kV = None
        print(self.model)
        if self.model == 'A':
            volts2 = (kV * 1000.0 + 143.66) / 1.0158
            volts = int(4095 * (4200.0 - volts2) / 2200.0)
            f42kV = volts.to_bytes(2, 'little')
        elif self.model == 'B':
            volts2 = (kV * 1000.0 + 2.5435) / 1.012
            volts = int(4095 * (4100.0 - volts2) / 2200.0)
            f42kV = volts.to_bytes(2, 'little')
        cmd = [esc.to_bytes(1,'little'), w.to_bytes(1, 'little'),
               nr.to_bytes(1, 'little'), kiek.to_bytes(1,'little'),
               add.to_bytes(1,'little'), f42kV[0].to_bytes(1, 'little'), f42kV[1].to_bytes(1,'little')]
        cmd_ = b''.join(cmd)#+f42kV
        cmd_crc = ComputeHash(cmd_)
        cmd_b = b''.join(cmd)+cmd_crc
        n = self.port.write(cmd_b)
        # if n is not None and n > 0:
        #     pass
        time.sleep(1)
        ret = self.port.read(22) #koks ilgis? 22 atseit?
        crc_status, crcr, crc_r = CompareHash(ret)
        ErrCode = self.crcErr[ret[-5]]
        cmdNr = ret[-6]
        cmdRep = ret[-7]
        iin = ret[-8]
        crc_v = ret[-10:-8]
        return  crc_status, crcr, crc_r, ErrCode, cmdNr, cmdRep, crc_v, cmd_crc
    #


    def countNi(self, Ts:int, Cth:int, Tz=0, Tq=0, Vq=0, cmdnr=1):
        '''
        Prašymas pradėti skaičiavimą.
        Esc  s nr Ts Tz Tq Cth Vq  CRC32

        Skaičiavimo trukme Ts (baitas), po 100ms (max 25.5s). 0 reiškia pastovaus skaičiavimo paleidimą. Po skaičiavimo trukmės pasibaigimo skaitiklis nėra nunulinamas ir skaičiuoja toliau, o jo rezultatus galima nusiskaityti atmintyje.
        Trumpinimo trukmė po gesinimo Tz (baitas), po 10us (10us-2.55 ms). Trumpinimas prasideda  užfiksavus impulsą, tačiau laiko skaičiavimas pradedamas tik pasibaigus Tq. Taigi visa trumpinimo trukmė yra Tq+Tz.
        Gesinimo trukmė Tq (2 baitai), po 10us (10us-0.65s). Pasileidžia užfiksavus impulsą. Jei=0, gesinimo nėra.
        Komparatoriaus suveikimo riba Cth (baitas), 0-0xff (0-3.3V)
        Gesinimo įtampa Vq (baitas), 0-0xff (0-100V)

        Atsakymas išsiunčiamas suskaičiavus. Išimtis: jei trukmė =0x00, atsakymas siunčiamas išsyk, o skaičiavimas stabdomas nebus. Skaitiklį tuomet galima nuskaityti iš atminties.
        Specifiniai_duomenys:
        Ni: einama impulsų skaitiklio vertė. (4 baitai)
        :return:  statusas, įrašytų bitų kiekis, error text (OK arba kitas tekstas)
        '''
        esc = 0x1b.to_bytes(1,'little')
        s = 0x73.to_bytes(1,'little')
        nr = cmdnr.to_bytes(1, 'little')
        Tsb = (Ts*10).to_bytes(1, 'little')
        Tzb = (Tz*100).to_bytes(1,'little')
        Tqb = (Tq*100).to_bytes(2, 'little') #!
        Vqb = int(Vq/0.392).to_bytes(1, 'little')
        Cthb = int(Cth).to_bytes(1, 'little')
        cmd_ = [esc, s, nr, Tsb, Tzb,Tqb[1].to_bytes(1,'little'), Tqb[0].to_bytes(1,'little'), Cthb, Vqb]
        cmd = b''.join(cmd_)
        crc = ComputeHash(cmd)
        cmdb = cmd+crc
        try:
            n = self.port.write(cmdb)
            return True, n, 'OK'
        except Exception as ex:
            return False, -1, str(ex) 
        pass
    
    def readNi(self):
        '''Atsakymas išsiunčiamas suskaičiavus. Išimtis: jei trukmė =0x00, atsakymas siunčiamas išsyk, o skaičiavimas stabdomas nebus. Skaitiklį tuomet galima nuskaityti iš atminties.
        Specifiniai_duomenys: 
        Ni: einama impulsų skaitiklio vertė. (4 baitai)
        Return: Ni, statusas, ErrCode, code, crc_gautas, crc_apsk'''
        data = self.port.read(size=26) #kodėl 26 baitai? 4 pradžia, 4 duomenys, 14 spec + 4 crc32 = 26b
        statusas, ErrCode, code, crc_gautas, crc_apsk = self.lastBytes(data)
        Nib = data[4:8]
        Ni = int.from_bytes(Nib, 'little')
        return Ni, statusas, ErrCode, code, crc_gautas, crc_apsk, data
        pass
    
    def lastBytes(self, data):
        '''
        statusas: True/False 
        ErrCode: str -> tekstinis pranešimas klaidos
        code: [0,1,2,3,4,5,6] - skaitmeninis klaidos kodas 
        crc_gautas, crc_apsk : CRC kodai
        Ne visi baitai apdorojami!
        '''
        statusas, crc_gautas, crc_apsk = CompareHash(data)
        ErrCode = self.crcErr.get(data[-5], '-0:'+str(data[-5]))
        if '-0:' in ErrCode:
            print(data, int.from_bytes(data[-5], 'little'), '<==', sep='\n')
        return statusas, ErrCode, int(data[-5]), crc_gautas, crc_apsk
        pass
    
# Atsakymas

# Pradžia		0xA5, 0x5A (Yen sign,Z)
# Ilgis		2 baitai
# Parsiunčiami duomenys	viso: ilgis-4 baitai
# CRC32		Visų baitų


# Parsiunčiami duomenys yra sudaryti iš specifinių_duomenų(kiekis priklauso nuo komandos)
# ir statuso_duomenų(14 baitų).

# Statuso_duomenys:

# 3:0	Tm dabar_vykstančio skaičiavimo trukme po 10ms 
# 5:4*	00HV45_15  šaltinio įtampa 0-4.5kV skalėje (0..0x7fff). Kombinuota iš 00HV45 ir 45HV35
# 7:6	Iin vidutinė srovė
# 9:8	kodo_crc  (vietoje versijos numerio)	
# 10	Statusas
# 	.0	I50nA500	įėjimo srovės skalė. 0/1 atitinka 50nA/500nA
# 11	Pakartota komanda
# 12	Pakartotas nr
# 13	Err; klaidos kodas:
# 	0 ok
# 	1 CRC klaida
# 	2 bloga komanda
# 	3 blogas parametras
# 	4 protokolo taimoutas (laikas tarp siuntos baitų >0.1s)
# 	5 U per maža
# 	6 U per didelė







