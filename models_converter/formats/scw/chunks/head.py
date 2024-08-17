from . import Chunk


class HEAD(Chunk):
    chunk_name = "HEAD"

    def __init__(self):
        self.version: int = 2
        self.frame_rate: int = 30
        self.first_frame: int = 0
        self.last_frame: int = 0
        self.materials_file: str | None = None
        self.v3: int = 0

    def parse(self, buffer: bytes, header=None) -> None:
        super().parse(buffer)

        self.version = self.read_unsigned_int16()
        self.frame_rate = self.read_unsigned_int16()
        self.first_frame = self.read_unsigned_int16()
        self.last_frame = self.read_unsigned_int16()
        self.materials_file = self.read_string()
        if self.version >= 1:
            self.v3 = self.read_unsigned_int8()

    def encode(self, header) -> None:
        super().encode()

        self.version = 2

        self.write_unsigned_int16(self.version)
        self.write_unsigned_int16(self.frame_rate)
        self.write_unsigned_int16(self.first_frame)
        self.write_unsigned_int16(self.last_frame)
        self.write_string(self.materials_file)
        if self.version >= 1:
            self.write_unsigned_int8(0)

        self.length = len(self.buffer)
