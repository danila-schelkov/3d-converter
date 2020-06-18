from scw.utils.reader import Reader
from scw.utils.writer import Writer


class Decoder(Reader):
    def __init__(self, initial_bytes: bytes, header: dict):
        super().__init__(initial_bytes)


class Encoder(Writer):
    def __init__(self):
        super().__init__()
