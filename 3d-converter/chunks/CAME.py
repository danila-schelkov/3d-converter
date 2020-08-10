<<<<<<< Updated upstream:3d-converter/chunks/CAME.py
from utils.reader import Reader
from utils.writer import Writer
=======
from ..utils.reader import Reader
from ..utils.writer import Writer
from .chunk import Chunk
>>>>>>> Stashed changes:models_converter/chunks/CAME.py


class Decoder(Chunk, Reader):
    def __init__(self, header: dict):
        super().__init__(header)

<<<<<<< Updated upstream:3d-converter/chunks/CAME.py
        self.readed = {}
=======
    def parse(self, initial_bytes: bytes):
        super().__init__(initial_bytes)
>>>>>>> Stashed changes:models_converter/chunks/CAME.py


class Encoder(Chunk, Writer):
    def __init__(self):
        super().__init__()
        self.name = 'CAME'

    def encode(self, data: dict):
        self.data = data
        self.length = len(self.buffer)
