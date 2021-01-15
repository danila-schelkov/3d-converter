from . import Chunk


class CAME(Chunk):
    def __init__(self, header=None):
        super().__init__(header)
        self.chunk_name = 'CAME'

    def parse(self, buffer: bytes):
        super().parse(buffer)

        setattr(self, 'name', self.readString())
        setattr(self, 'v1', self.readFloat())
        setattr(self, 'xFov', self.readFloat())
        setattr(self, 'aspectRatio', self.readFloat())
        setattr(self, 'zNear', self.readFloat())
        setattr(self, 'zFar', self.readFloat())

    def encode(self):
        super().encode()

        self.writeString(getattr(self, 'name'))
        self.writeFloat(getattr(self, 'v1'))
        self.writeFloat(getattr(self, 'xFov'))
        self.writeFloat(getattr(self, 'aspectRatio'))
        self.writeFloat(getattr(self, 'zNear'))
        self.writeFloat(getattr(self, 'zFar'))

        self.length = len(self.buffer)
