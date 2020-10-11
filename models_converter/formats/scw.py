import binascii

from ..chunks import *
from ..chunks.chunk import Chunk
from ..utils.reader import Reader


def _(*args):
    print('[ScwUtils]', end=' ')
    for arg in args:
        print(arg, end=' ')
    print()


class Writer:
    def __init__(self):
        self.writen = b'SC3D'

    def write(self, data: dict):

        header = data['header']
        head = HEAD()
        head.from_dict(header)

        self.write_chunk(head)

        # TODO: materials
        # for material in data['materials']:
        #     mate = MATE(header)
        #     mate.from_dict(material)
        #
        #     self.write_chunk(mate)

        for geometry in data['geometries']:
            geom = GEOM(header)
            geom.from_dict(geometry)

            self.write_chunk(geom)

        # TODO: cameras
        for camera in data['cameras']:
            came = CAME(header)
            came.from_dict(camera)

            self.write_chunk(came)

        node = NODE(header)
        node.from_dict({'nodes': data['nodes']})

        self.write_chunk(node)

        wend = WEND()

        self.write_chunk(wend)

    def write_chunk(self, chunk: Chunk):
        chunk.encode()

        self.writen += chunk.length.to_bytes(4, 'big') + chunk.chunk_name.encode('utf-8') + chunk.buffer
        self.writen += binascii.crc32(chunk.chunk_name.encode('utf-8') + chunk.buffer).to_bytes(4, 'big')


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
