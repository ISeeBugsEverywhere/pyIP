import zlib

def ComputeHash(buffer):
    h = zlib.crc32(buffer)
    h_ = h.to_bytes(4, 'little')
    return h_


def CompareHash(buffer):
    crc = buffer[-4:]
    data = buffer[:-4]
    crc_ = ComputeHash(data)
    return crc == crc_, crc, crc_