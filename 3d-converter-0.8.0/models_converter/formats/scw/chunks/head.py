from . import Chunk


class HEAD(Chunk):
    def __init__(self, header=None):
        super().__init__(header)
        self.chunk_name = 'HEAD'

    def parse(self, buffer: bytes):
        super().parse(buffer)

        setattr(self, 'version', self.readUShort())
        setattr(self, 'frame_rate', self.readUShort())
        setattr(self, 'v1', self.readUShort())
        setattr(self, 'v2', self.readUShort())
        setattr(self, 'materials_file', self.readString())
        if self.get('version') == 2:
            setattr(self, 'v3', self.readUByte())

    def encode(self):
        super().encode()

        self.writeUShort(2)  # getattr(self, 'version')
        self.writeUShort(getattr(self, 'frame_rate'))
        self.writeUShort(0)  # getattr(self, 'v1')
        self.writeUShort(249)  # getattr(self, 'v2')
        self.writeString(getattr(self, 'materials_file'))
        self.writeUByte(0)  # getattr(self, 'v3')

        self.length = len(self.buffer)
