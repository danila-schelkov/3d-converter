from ..universal import Scene
from ...interfaces import ParserInterface
from ...utilities.reader import Reader
from .chunks import *


class Parser(ParserInterface, Reader):
    def __init__(self, file_data: bytes):
        Reader.__init__(self, file_data)

        self.file_data = file_data
        self.scene = Scene()
        self.chunks = []

        self.header = None

        file_magic = self.read(4)
        if file_magic != b'SC3D':
            raise TypeError('File Magic isn\'t "SC3D"')

    def parse(self):
        self._split_chunks()

        for chunk in self.chunks:
            chunk_name = chunk['chunk_name']
            chunk_data = chunk['data']

            if chunk_name == 'HEAD':
                head = HEAD()
                head.parse(chunk_data)

                self.header = head
            elif chunk_name == 'MATE':
                mate = MATE(self.header)
                mate.parse(chunk_data)
                self.scene.add_material(mate)
            elif chunk_name == 'GEOM':
                geom = GEOM(self.header)
                geom.parse(chunk_data)
                self.scene.add_geometry(geom.geometry)
            elif chunk_name == 'CAME':
                came = CAME(self.header)
                came.parse(chunk_data)
                self.scene.add_camera(came.camera)
            elif chunk_name == 'NODE':
                node = NODE(self.header)
                node.parse(chunk_data)
                self.scene.get_nodes().extend(node.nodes)
            elif chunk_name == 'WEND':
                wend = WEND()
                wend.parse(chunk_data)
            else:
                raise TypeError(f'Unknown chunk: {chunk_name}')

    def _split_chunks(self):
        # len(Chunk Length) + len(Chunk Name) + len(Chunk CRC)
        while len(self.file_data[self.tell():]) >= 12:
            chunk_length = self.readUInt32()
            chunk_name = self.readChars(4)
            chunk_data = self.read(chunk_length)
            chunk_crc = self.readUInt32()

            self.chunks.append({
                'chunk_name': chunk_name,
                'data': chunk_data,
                'crc': chunk_crc
            })
