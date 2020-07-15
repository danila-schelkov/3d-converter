from utils.reader import Reader
from utils.writer import Writer


class Decoder(Reader):
    def __init__(self, initial_bytes: bytes):
        super().__init__(initial_bytes)

        # Variables
        self.readed = {}
        # Variables


class Encoder(Writer):
    def __init__(self):
        super().__init__()
        self.name = 'WEND'

        self.encode()

        self.length = len(self.buffer)

    def encode(self):
        pass
