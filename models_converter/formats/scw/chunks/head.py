from . import Chunk


class HEAD(Chunk):
    def __init__(self, header=None):
        super().__init__(header)
        self.chunk_name = 'HEAD'

        self.version: int = 2
        self.frame_rate: int = 30
        self.first_frame: int = 0
        self.last_frame: int = 0
        self.materials_file: str or None = None
        self.v3: int = 0

    def parse(self, buffer: bytes):
        super().parse(buffer)

        self.version = self.readUShort()
        self.frame_rate = self.readUShort()
        self.first_frame = self.readUShort()
        self.last_frame = self.readUShort()
        self.materials_file = self.readString()
        if self.version >= 1:
            self.v3 = self.readUByte()

    def encode(self):
        super().encode()

        self.version = 2

        self.writeUShort(self.version)
        self.writeUShort(self.frame_rate)
        self.writeUShort(self.first_frame)
        self.writeUShort(self.last_frame)
        self.writeString(self.materials_file)
        if self.version >= 1:
            self.writeUByte(0)

        self.length = len(self.buffer)
