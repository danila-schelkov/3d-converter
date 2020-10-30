from ...utils.reader import Reader
from .chunks import *


class Parser(Reader):
    def __init__(self, file_data: bytes):
        super().__init__(file_data)
        self.file_data = file_data
        self.parsed = {
            'header': {},
            'materials': [],
            'geometries': [],
            'cameras': [],
            'nodes': []
        }
        self.chunks = []

        file_magic = self.read(4)
        if file_magic != b'SC3D':
            raise TypeError('File Magic isn\'t "SC3D"')

    def split_chunks(self):
        # len(Chunk Length) + len(Chunk Name) + len(Chunk CRC)
        while len(self.file_data[self.tell():]) >= 12:
            chunk_length = self.readUInt32()
            chunk_name = self.readChar(4)
            chunk_data = self.read(chunk_length)
            chunk_crc = self.readUInt32()

            self.chunks.append({
                'chunk_name': chunk_name,
                'data': chunk_data,
                'crc': chunk_crc
            })

    def parse(self):
        for chunk in self.chunks:
            chunk_name = chunk['chunk_name']
            chunk_data = chunk['data']

            if chunk_name == 'HEAD':
                head = HEAD()
                head.parse(chunk_data)

                self.parsed['header'] = head.to_dict()
            elif chunk_name == 'MATE':
                mate = MATE(self.parsed['header'])
                mate.parse(chunk_data)
                self.parsed['materials'].append(mate.to_dict())
            elif chunk_name == 'GEOM':
                geom = GEOM(self.parsed['header'])
                geom.parse(chunk_data)
                self.parsed['geometries'].append(geom.to_dict())
            elif chunk_name == 'CAME':
                came = CAME(self.parsed['header'])
                came.parse(chunk_data)
                self.parsed['cameras'].append(came.to_dict())
            elif chunk_name == 'NODE':
                node = NODE(self.parsed['header'])
                node.parse(chunk_data)
                self.parsed['nodes'] = node.to_dict()['nodes']
            elif chunk_name == 'WEND':
                wend = WEND()
                wend.parse(chunk_data)
            else:
                raise TypeError(f'Unknown chunk: {chunk_name}')
