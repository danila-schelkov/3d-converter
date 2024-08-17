from typing import ClassVar

from ....utilities.reader import Reader
from ....utilities.writer import Writer


class Chunk(Writer, Reader):
    chunk_name: ClassVar[str] = "CHUNK"

    def __init__(self):
        self.length = 0

    def parse(self, buffer: bytes, *args) -> None:
        Reader.__init__(self, buffer, "big")

    def encode(self, *args) -> None:
        Writer.__init__(self, "big")

        self.length = len(self.buffer)
