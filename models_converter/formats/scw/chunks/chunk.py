from ....utilities.reader import Reader
from ....utilities.writer import Writer


class Chunk(Writer, Reader):
    def __init__(self, header):
        super().__init__()

        self.header = header
        self.chunk_name = ''

        self.buffer = b''
        self.length = 0

    def parse(self, buffer: bytes):
        Reader.__init__(self, buffer, 'big')

    def encode(self):
        Writer.__init__(self, 'big')

        self.length = len(self.buffer)
