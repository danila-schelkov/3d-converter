<<<<<<< Updated upstream:3d-converter/chunks/HEAD.py
from utils.reader import Reader
from utils.writer import Writer
=======
from ..utils.reader import Reader
from ..utils.writer import Writer
from .chunk import Chunk
>>>>>>> Stashed changes:models_converter/chunks/HEAD.py


class Decoder(Chunk, Reader):
    def __init__(self, header: dict):
        super().__init__(header)

<<<<<<< Updated upstream:3d-converter/chunks/HEAD.py
        # Variables
        self.readed = {}
        # Variables
=======
    def parse(self, initial_bytes: bytes):
        super().__init__(initial_bytes)
>>>>>>> Stashed changes:models_converter/chunks/HEAD.py

        version = self.readUShort()
        frame_rate = self.readUShort()
        self.readUShort()
        self.readUShort()
        materials_file = self.readString()
        self.readUByte()

        self.readed['version'] = version
        self.readed['frame_rate'] = frame_rate
        self.readed['materials_file'] = materials_file


class Encoder(Chunk, Writer):
    def __init__(self):
        super().__init__()
        self.name = 'HEAD'

    def encode(self, data: dict):
        self.data = data

<<<<<<< Updated upstream:3d-converter/chunks/HEAD.py
    def encode(self):
        self.writeUShort(self.data['version'])  # version
=======
        self.writeUShort(2)  # version  # self.data['version']
>>>>>>> Stashed changes:models_converter/chunks/HEAD.py
        self.writeUShort(self.data['frame_rate'])  # frame rate
        self.writeUShort(0)
        self.writeUShort(249)
        self.writeString(self.data['materials_file'])  # materials file
        self.writeUByte(0)

        self.length = len(self.buffer)
