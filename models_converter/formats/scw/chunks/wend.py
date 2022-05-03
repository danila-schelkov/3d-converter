from . import Chunk


class WEND(Chunk):
    def __init__(self, header=None):
        super().__init__(header)
        self.chunk_name = 'WEND'
