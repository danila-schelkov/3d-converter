class Chunk:
    def __init__(self, header=None):
        if header is None:
            header = {}
        self.header = header

        self.buffer = b''  # Data Buffer
        self.chunk_name = ''  # Chunk Name etc. HEAD, MATE, GEOM, and other
        self.data = {}  # Parsed File Data
        self.length = 0  # Length of buffer

        self.parsed = {}  # Union of Parsed Data

    def parse(self, initial_bytes: bytes):
        pass

    def encode(self, data: dict):
        pass
