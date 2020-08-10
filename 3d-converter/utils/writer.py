from struct import pack


class Writer:
    def __init__(self):
        super(Writer, self).__init__()
        self.buffer = b''

    def writeUInteger(self, integer: int, length: int = 1):
        self.buffer += integer.to_bytes(length, 'big', signed=False)

    def writeInteger(self, integer: int, length: int = 1):
        self.buffer += integer.to_bytes(length, 'big', signed=True)

    def writeUInt64(self, integer: int):
        self.buffer += pack('>Q', integer)

    def writeInt64(self, integer: int):
        self.buffer += pack('>q', integer)

    def writeFloat(self, floating: float):
        self.buffer += pack('>f', floating)

    def writeUInt32(self, integer: int):
        self.buffer += pack('>I', integer)

    def writeInt32(self, integer: int):
        self.buffer += pack('>i', integer)

    def writeUInt16(self, integer: int):
        self.buffer += pack('>H', integer)

    def writeInt16(self, integer: int):
        self.buffer += pack('>h', integer)

    def writeUInt8(self, integer: int):
        self.buffer += pack('>B', integer)

    def writeInt8(self, integer: int):
        self.buffer += pack('>b', integer)

    def writeBool(self, boolean: bool):
        self.buffer += pack('>?', boolean)

<<<<<<< Updated upstream:3d-converter/utils/writer.py
    def writeUInteger(self, integer: int, length: int = 1):
        return integer.to_bytes(length, 'big', signed=False)

    def writeInteger(self, integer: int, length: int = 1):
        return integer.to_bytes(length, 'big', signed=True)
=======
    def writeNormalizedUInt16(self, floating: float):
        self.writeUInt16(round(floating * 65535))

    def writeNormalizedInt16(self, floating: float):
        self.writeInt16(round(floating * 32512))

    writeUInt = writeUInteger
    writeInt = writeInteger
>>>>>>> Stashed changes:models_converter/utils/writer.py

    writeULong = writeUInt64
    writeLong = writeInt64

    writeUShort = writeUInt16
    writeShort = writeInt16

    writeUByte = writeUInt8
    writeByte = writeInt8

    writeNUShort = writeNormalizedUInt16
    writeNShort = writeNormalizedInt16

    def writeChar(self, string: str):
        for char in list(string):
            self.buffer += char.encode('utf-8')

    def writeString(self, string: str):
        encoded = string.encode('utf-8')
        self.writeUShort(len(encoded))
        self.buffer += encoded
