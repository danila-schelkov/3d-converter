from utils import Reader
from utils import Writer


class Decoder(Reader):
    def __init__(self, initial_bytes: bytes, header: dict):
        super().__init__(initial_bytes)


class Encoder(Writer):
    def __init__(self, info: dict):
        super().__init__()
