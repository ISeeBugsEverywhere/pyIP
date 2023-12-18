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
    def __init__(self, A):
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
            ErrCode = r_[-5]
            cmdNr = r_[-6]
            cmdRep = r_[-7]
            scaleStatus = int(r_[-8])
            return cr, crcr, crc_r, ErrCode, cmdNr, cmdRep, scaleStatus, scaleStatusd[scaleStatus]
        except Exception as ex:
            print('::EX:{}::'.format(str(ex)))


    def setVoltage(self, kV, cmd_nr):
        '''
        Rašymui/skaitymui (iki 0x0f):

1:0	42Vset35:  nustatyta HV išėjimo įtampa. 0 atitinka 4.2kV, 0xfff atitinka 2.0 kV.
3:2	Kp:  proporcingumo koeficientas dėl išėjimo PWM apskaičiavimo: PWM= Kp* impulsų_kiekis_pe_1_s / 0x1000.
4	Vq: gesinimo įtampa 0-0xff (0-100V)
//konversija:
            //x = 4095*(4,2kV-U kV)/2,2kV;
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
        kiek = 2+1

        pass

    def countNi(self, Ts, Cth, Tz=0, Tq=0, Vq=0, nr=1):
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
        :return:
        '''
        pass







