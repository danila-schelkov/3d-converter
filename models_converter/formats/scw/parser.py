from typing import NamedTuple

from ..universal import Scene
from ...interfaces import ParserInterface
from ...utilities.reader import Reader
from .chunks import *


class ChunkData(NamedTuple):
    type: str
    data: bytes
    crc: int


class Parser(ParserInterface):
    def __init__(self, file_data: bytes):
        self.file_data = file_data
        self.chunks: list[ChunkData] = []

        self.header: HEAD | None = None

    def parse(self):
        self.scene: Scene = Scene()

        reader = Reader(self.file_data, "big")
        file_magic = reader.read(4)
        if file_magic != b"SC3D":
            raise TypeError('File Magic isn\'t "SC3D"')

        self._split_chunks(reader)

        for chunk in self.chunks:
            if chunk.type == "HEAD":
                head = HEAD()
                head.parse(chunk.data)
                self.header = head
            elif chunk.type == "MATE":
                mate = MATE()
                mate.parse(chunk.data, self.header)

                assert mate.material is not None
                self.scene.add_material(mate.material)
            elif chunk.type == "GEOM":
                geom = GEOM()
                geom.parse(chunk.data, self.header)

                assert geom.geometry is not None
                self.scene.add_geometry(geom.geometry)
            elif chunk.type == "CAME":
                came = CAME()
                came.parse(chunk.data, self.header)

                assert came.camera is not None
                self.scene.add_camera(came.camera)
            elif chunk.type == "NODE":
                node = NODE()
                node.parse(chunk.data, self.header)
                self.scene.get_nodes().extend(node.nodes)
            elif chunk.type == "WEND":
                wend = WEND()
                wend.parse(chunk.data)
            else:
                raise TypeError(f"Unknown chunk: {chunk.type}")

    def _split_chunks(self, reader: Reader):
        # len(Chunk Length) + len(Chunk Name) + len(Chunk CRC)
        while reader.tell() <= len(self.file_data) - 12:
            chunk_length = reader.read_unsigned_int32()
            chunk = ChunkData(
                reader.read(4).decode(),
                reader.read(chunk_length),
                reader.read_unsigned_int32(),
            )

            self.chunks.append(chunk)
