from GUI.SerialPortWidget.SerialPortUI import Ui_serialPortWidget
import sys
import glob
import serial
from PyQt5 import QtWidgets

class serialPortWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(serialPortWidget, self).__init__()
        self.ui = Ui_serialPortWidget()
        self.ui.setupUi(self)
        self.__scan_ports__()
        self.__fill_up__()
        pass

    def __serial_ports__(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
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

    def __scan_ports__(self):
        """
        Scans ports and fills up all them into comPortBox
        :return:
        """
        ports = self.__serial_ports__()
        for i in ports:
            self.ui.comPortBox.addItem(str(i))
            pass
        pass

    def __fill_up__(self):
        baudrates = [110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000 ,256000]
        for i in baudrates:
            self.ui.baudRateBox.addItem(str(i))
            pass
        #stop bits:
        #data bits
        #parity:
        pass