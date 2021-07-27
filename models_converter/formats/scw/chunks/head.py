from . import Chunk


class HEAD(Chunk):
    def __init__(self, header=None):
        super().__init__(header)
        self.chunk_name = 'HEAD'

    def parse(self, buffer: bytes):
        super().parse(buffer)

        setattr(self, 'version', self.readUShort())
        setattr(self, 'frame_rate', self.readUShort())
        setattr(self, 'first_frame', self.readUShort())
        setattr(self, 'last_frame', self.readUShort())
        setattr(self, 'materials_file', self.readString())
        if self.get('version') >= 1:
            setattr(self, 'v3', self.readUByte())

    def encode(self):
        super().encode()

        setattr(self, 'version', 2)

        self.writeUShort(getattr(self, 'version'))
        self.writeUShort(getattr(self, 'frame_rate'))
        self.writeUShort(getattr(self, 'first_frame'))
        self.writeUShort(getattr(self, 'last_frame'))
        self.writeString(getattr(self, 'materials_file'))
        if self.get('version') >= 1:
            self.writeUByte(0)  # getattr(self, 'v3')

        self.length = len(self.buffer)
