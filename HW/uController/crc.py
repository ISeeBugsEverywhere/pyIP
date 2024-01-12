import zlib

def ComputeHash(buffer):
    h = zlib.crc32(buffer)
    h_ = h.to_bytes(4, 'little')
    return h_


def CompareHash(buffer):
    '''
    crc statusas (True/False); CRC gautas, CRC apskaičiuotas
    '''
    crc_gautas = buffer[-4:]
    data = buffer[:-4]
    crc_apskaiciuotas = ComputeHash(data)
    return crc_gautas == crc_apskaiciuotas, crc_gautas, crc_apskaiciuotas