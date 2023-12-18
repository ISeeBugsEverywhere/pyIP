import serial
import os, sys, time
from Config.ipcfg import CFG

import glob
import subprocess

# out = subprocess.run(['udevadm', 'info', '-r', '-q', 'all', i], capture_output=True, text=True)
def get_serial_ports():
    result = {}
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
        result = dict.fromkeys(ports)
        k = 1
        for i in result.keys():
            result[i] = "COM{}".format(k)
            k = k + 1
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ttyUBSs = glob.glob('/dev/ttyUSB*')
        ACTMs = glob.glob('/dev/ttyA*')
        if len(ACTMs) > 0:
            ttyUBSs.extend(ACTMs)
        for i in ttyUBSs:
            dev = {}
            out = subprocess.run(['udevadm', 'info', '-r', '-q', 'all', i], capture_output=True, text=True)
            r_ = out.stdout
            c = out.returncode
            l_ = r_.splitlines()
            vid = ''
            mid = ''
            for i_ in l_:
                if 'DEVNAME' in i_:
                    d, n = i_.split("=")
                    dev['devname'] = n
                if 'ID_MODEL_FROM_DATABASE' in i_:
                    m, n = i_.split('=')
                    dev['idModel'] = n
                if "ID_MODEL_ID" in i_:
                    m, n = i_.split('=')
                    mid = n
                if "ID_VENDOR_ID" in i_:
                    m, n = i_.split('=')
                    vid = n
            result[dev['idModel']+ " ({}:{})".format(vid, mid)] = dev['devname']
    return result


def get_port_param_dct(section:str, cfg:CFG):
    p_ = {'baudrate': 9600,
             'bytesize': 8,
             'parity': 'N',
             'stopbits': 1,
             'xonxoff': False,
             'dsrdtr': False,
             'rtscts': False,
             'timeout': None,
             'write_timeout': None,
             'inter_byte_timeout': None}
    for key in p_.keys():
        r_ = cfg.parser[section][key]
        if r_ == 'None':
            p_[key] = None
        elif r_.isnumeric():
            p_[key] = int(r_)
        elif r_ == 'False':
            p_[key] = False
        elif r_ == 'True':
            p_[key] = True
        elif r_.isalpha():
            p_[key] = r_
        else:
            p_[key] = r_
    return p_

class ArdParser():
    def __init__(self):
        self.ARDSTR = ''

    def fillArdStr(self, s:str):
        self.ARDSTR = self.ARDSTR + s.replace("\n", '').replace('\r','')

    def analyzeArd(self, s:str):
        '''
        s: arduino answer
        GAS:xxx;tt.tt;O2:zz.zz:O2:!;O22:xx.yy:O22:!
        :return o2, t, o22, ch4, status_msg, code, dht, rem
        '''
        self.fillArdStr(s)
        o22 = -1
        o2 = -1
        t = -99.99
        ch4 = -1
        status_msg = 'msg?'
        code = -1 #0 - o2, 1- dht, 2 - rem
        dht = -1
        rem = 'rem?'
        if 'GAS:' in self.ARDSTR and ':O2:!' in self.ARDSTR:
            gasPos = self.ARDSTR.index('GAS:')
            o2Pos = self.ARDSTR.index(':O2:!')
            if gasPos < o2Pos:
                sub_str = self.ARDSTR[gasPos:o2Pos+1]
                if 'O22:' in self.ARDSTR and ':O22:!' in self.ARDSTR:
                    #čia yra ir antras O2 detektorius:
                    o22Pos = self.ARDSTR.index('O22:')
                    O22End = self.ARDSTR.index(':O22:!')
                    o22 = float(self.ARDSTR[o22Pos:O22End+1])
                values = sub_str.split(';')
                ch4 = values[0].replace('GAS:','')
                o2 = values[2][2:8]
                t = values[1]
                status_msg = "O2, OK"
                code = 0
                self.ARDSTR = self.ARDSTR.replace(sub_str, '')
        if "REM:" in self.ARDSTR and ':REM:!' in self.ARDSTR:
            remStart = self.ARDSTR.index('REM:')
            remEnd = self.ARDSTR.index(':REM:!')
            if remStart < remEnd:
                rem_ = self.ARDSTR[remStart:remEnd+6]
                status_msg = 'rem message'
                rem = rem_[4:-6]
                code = 2
                self.ARDSTR = self.ARDSTR.replace(rem_, '')
        if 'DHT:' in self.ARDSTR and ':DHT:!' in self.ARDSTR:
            dhtStart = self.ARDSTR.index('DHT:')
            dhtEnd = self.ARDSTR.index(':DHT:!')
            if dhtStart < dhtEnd:
                dht_ = self.ARDSTR[dhtStart:dhtEnd+6]
                dht = dht_[4:-6]
                status_msg ='dht ok'
                code = 1
                self.ARDSTR = self.ARDSTR.replace(dht_, '')
        return o2, t, o22, ch4, status_msg, code, dht, rem
        pass



