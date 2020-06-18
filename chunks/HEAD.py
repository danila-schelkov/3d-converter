from scw.utils.reader import Reader
from scw.utils.writer import Writer


class Decoder(Reader):
    def __init__(self, initial_bytes: bytes):
        super().__init__(initial_bytes)

        # Variables
        self.readed = {}
        # Variables

        version = self.readUShort()
        self.readUShort()
        self.readUShort()
        self.readUShort()
        materials_file = self.readString()
        self.readUByte()

        self.readed['version'] = version
        self.readed['materials_file'] = materials_file


class Encoder(Writer):
    def __init__(self, info: dict):
        super().__init__()
        self.writeUShort(info['version'])  # version
        self.writeUShort(30)
        self.writeUShort(0)
        self.writeUShort(249)
        self.writeString(info['materials_file'])  # materials file
        self.writeUByte(0)
