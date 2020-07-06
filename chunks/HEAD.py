from utils import Reader
from utils import Writer


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
    def __init__(self, data: dict):
        super().__init__()
        self.name = 'HEAD'
        self.data = data

        self.encode()

        self.length = len(self.buffer)

    def encode(self):
        self.writeUShort(self.data['version'])  # version
        self.writeUShort(30)
        self.writeUShort(0)
        self.writeUShort(249)
        self.writeString(self.data['materials_file'])  # materials file
        self.writeUByte(0)
