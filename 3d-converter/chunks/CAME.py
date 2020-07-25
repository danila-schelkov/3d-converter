from utils.reader import Reader
from utils.writer import Writer


class Decoder(Reader):
    def __init__(self, initial_bytes: bytes, header: dict):
        super().__init__(initial_bytes)

        self.readed = {}


class Encoder(Writer):
    def __init__(self, data: dict):
        super().__init__()
        self.name = 'WEND'
        self.data = data

        self.encode()

        self.length = len(self.buffer)

    def encode(self):
        pass
