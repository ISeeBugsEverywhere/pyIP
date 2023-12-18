import usb.core
import usb.backend.libusb1
import time





# hardcoded, for CS260 USB only
# CONSTS:
WADDR = 0x01  # address for writing
RADDR = 0x81  # address for reading
END = "\r\n"
SIZE = 64
DELAY = 1  # seconds


class Oriel():
    # VENDOR_ID = 0x0
    # PRODUCT_ID = 0x0
    def __init__(self, Vendor, Product):
        self.device = None
        self.VENDOR_ID = Vendor
        self.PRODUCT_ID = Product

    def setup(self):
        """
        setup a devce;
        return 0 on success
        1 otherwise;

        """
        status = 1
        self.device = usb.core.find(idVendor=self.VENDOR_ID, idProduct=self.PRODUCT_ID)
        if self.device is not None:
            usb.util.claim_interface(self.device, 0)
            status = 0
        return status  # if O.K. - return 0, else 1

    def gowave(self, wave, units="nm"):
        """
        go to wave, wave in nanometers
        or energy in eV
        return bytes written
        -1 if no bytes were written
        """
        bts = -1
        if units == "nm":
            bts = self.device.write(WADDR, "GOWAVE "+str(wave)+END)
        elif units.lower() == "ev":
            wv = 1239.75/float(wave)
            bts = self.device.write(WADDR, "GOWAVE "+str(round(wv, 2))+END)
        return bts

    def answer(self, size=SIZE):
        """
        reads and returns an answer from CS260
        reads until CR LF sequence
        returs string and original data
        default length is 32 bytes.
        """
        data = self.device.read(RADDR, size)
        bytes_str = ''
        for i in range(0, len(data)):
            if data[i] == 13 and data[i+1] == 10:
                break
            else:
                bytes_str = bytes_str + chr(data[i])
        return bytes_str

    def cmd(self, cmd, size=SIZE):
        """
        sends a cmd to CS260
        if cmd contains ? - reads and returns an answer,
        otherwise returns how many bytes were written.
        cmd uses a delay between  writing and reading,
        specified by DELAY variable, equal to 1 second.

        """
        answer = ''
        if "?" in cmd:
            bts = self.device.write(WADDR, cmd+END)
            time.sleep(DELAY)
            answer = self.answer(size)
        else:
            bts = self.device.write(WADDR, cmd+END)
            answer = str(bts)
        return answer

    def closeShutter(self):
        """
        closes a shutter
        """
        return self.cmd("SHUTTER C")
        pass

    def openShutter(self):
        """
        opens a shutter
        """
        return self.cmd("SHUTTER O")
        pass

    def shutter(self, size=SIZE):
        """
        gets and returns shutter status - closed or opened, c or o
        """
        status = self.cmd("SHUTTER?", size)
        return status
        pass

    def wave(self, size=SIZE):
        """
        reads and returns current wave position
        """
        wave = self.cmd("WAVE?", size)
        return wave
        pass

    def remove(self):
        """
        frees resource, removes device,
        it should be called before exiting an app.
        """
        usb.util.release_interface(self.device, 0)
        self.device = None
        pass

    # methods for testing purposes:

    def _cmd_(self, cmd, size=SIZE):
        """
        TESTING.

        RETURNS ANSWER AND RAW DATA
        """
        answer = ''
        if "?" in cmd:
            bts = self.device.write(WADDR, cmd+END)
            time.sleep(DELAY)
            answer = self._answer_(size)
        else:
            bts = self.device.write(WADDR, cmd+END)
            answer = str(bts)
        return answer
        pass

    def _answer_(self, size=SIZE):
        """
        TESTING

        RETURNS STRING AND RAW DATA
        """
        data = self.device.read(RADDR, size)
        bytes_str = ''
        for i in range(0, len(data)):
            if data[i] == 13 and data[i+1] == 10:
                break
            else:
                bytes_str = bytes_str + chr(data[i])
        return bytes_str, data
