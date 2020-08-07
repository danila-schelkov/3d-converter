from io import BufferedReader, BytesIO
from struct import unpack


class Reader(BufferedReader):
    def __init__(self, initial_bytes: bytes, endian: str = 'big'):
        super(Reader, self).__init__(BytesIO(initial_bytes))

        self.endian_str = endian
        if endian == 'big':
            self.endian = '>'
        elif endian == 'little':
            self.endian = '<'

    def readUInt64(self):
        return unpack(self.endian + 'Q', self.read(8))[0]

    def readInt64(self):
        return unpack(self.endian + 'q', self.read(8))[0]

    def readFloat(self):
        return unpack(self.endian + 'f', self.read(4))[0]

    def readUInt32(self):
        return unpack(self.endian + 'I', self.read(4))[0]

    def readInt32(self):
        return unpack(self.endian + 'i', self.read(4))[0]

    def readUInt16(self):
        return unpack(self.endian + 'H', self.read(2))[0]

    def readInt16(self):
        return unpack(self.endian + 'h', self.read(2))[0]

    def readUInt8(self):
        return unpack(self.endian + 'B', self.read(1))[0]

    def readInt8(self):
        return unpack(self.endian + 'b', self.read(1))[0]

    def readBool(self):
        return unpack(self.endian + '?', self.read(1))[0]

    def readUInteger(self, length: int = 1):
        return int.from_bytes(self.read(length), self.endian_str, signed=False)

    def readInteger(self, length: int = 1):
        return int.from_bytes(self.read(length), self.endian_str, signed=True)

    readULong = readUInt64
    readLong = readInt64

    readUShort = readUInt16
    readShort = readInt16

    readUByte = readUInt8
    readByte = readInt8

    readUInt = readUInteger
    readInt = readInteger

    def readChar(self, length: int = 1):
        return self.read(length).decode('utf-8')

    def readString(self):
        return self.readChar(self.readUShort())
