from ..utils.reader import Reader
from ..utils.writer import Writer


class Decoder(Reader):
    def __init__(self, initial_bytes: bytes):
        super().__init__(initial_bytes)

        # Variables
        self.readed = {}
        # Variables

        version = self.readUShort()
        frame_rate = self.readUShort()
        self.readUShort()
        self.readUShort()
        materials_file = self.readString()
        if version == 2:
            self.readUByte()

        self.readed['version'] = version
        self.readed['frame_rate'] = frame_rate
        self.readed['materials_file'] = materials_file


class Encoder(Writer):
    def __init__(self, data: dict):
        super().__init__()
        self.name = 'HEAD'
        self.data = data

        self.encode()

        self.length = len(self.buffer)

    def encode(self):
        self.writeUShort(2)  # version  # self.data['version']
        self.writeUShort(self.data['frame_rate'])  # frame rate
        self.writeUShort(0)
        self.writeUShort(249)
        self.writeString(self.data['materials_file'])  # materials file
        self.writeUByte(0)
