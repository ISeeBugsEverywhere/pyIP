import zlib

DefaultPolynomial = 0xedb88320
DefaultSeed = 0xffffffff

def ComputeHash(data):
    return zlib.crc32(data) & DefaultSeed #?
    pass

