from . import Chunk


class WEND(Chunk):
    def __init__(self, header=None):
        super().__init__(header)
        self.chunk_name = 'WEND'

    def parse(self, buffer: bytes):
        super().parse(buffer)

    def encode(self):
        super().encode()

        self.length = len(self.buffer)
