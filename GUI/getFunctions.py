import serial
import os, sys, time
import glob
from Config.ipcfg import CFG

def get_serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
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


