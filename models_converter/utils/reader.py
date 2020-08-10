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

    def readUInteger(self, length: int = 1) -> int:
        return int.from_bytes(self.read(length), self.endian_str, signed=False)

    def readInteger(self, length: int = 1) -> int:
        return int.from_bytes(self.read(length), self.endian_str, signed=True)

    def readUInt64(self) -> int:
        return unpack(self.endian + 'Q', self.read(8))[0]

    def readInt64(self) -> int:
        return unpack(self.endian + 'q', self.read(8))[0]

    def readFloat(self) -> float:
        return unpack(self.endian + 'f', self.read(4))[0]

    def readUInt32(self) -> int:
        return unpack(self.endian + 'I', self.read(4))[0]

    def readInt32(self) -> int:
        return unpack(self.endian + 'i', self.read(4))[0]

    def readUInt16(self) -> int:
        return unpack(self.endian + 'H', self.read(2))[0]

    def readInt16(self) -> int:
        return unpack(self.endian + 'h', self.read(2))[0]

    def readUInt8(self) -> int:
        return unpack(self.endian + 'B', self.read(1))[0]

    def readInt8(self) -> int:
        return unpack(self.endian + 'b', self.read(1))[0]

    def readBool(self) -> bool:
        return unpack(self.endian + '?', self.read(1))[0]

    def readNormalizedUInt16(self) -> float:
        floating = self.readUInt16() / 65535
        return floating

    def readNormalizedInt16(self) -> float:
        floating = self.readInt16() / 32512
        return floating

    readUInt = readUInteger
    readInt = readInteger

    readULong = readUInt64
    readLong = readInt64

    readUShort = readUInt16
    readShort = readInt16

    readUByte = readUInt8
    readByte = readInt8

    readNUShort = readNormalizedUInt16
    readNShort = readNormalizedInt16

    def readChar(self, length: int = 1) -> str:
        return self.read(length).decode('utf-8')

    def readString(self) -> str:
        return self.readChar(self.readUShort())
