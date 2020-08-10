import binascii

from ..chunks import *
from ..utils.reader import Reader


def _(*args):
    print('[ScwUtils]', end=' ')
    for arg in args:
        print(arg, end=' ')
    print()


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
                'name': chunk_name,
                'data': chunk_data,
                'crc': chunk_crc
            })

    def parse(self):
        for chunk_info in self.chunks:
            chunk_name = chunk_info['name']
            chunk_data = chunk_info['data']

            if chunk_name == 'HEAD':
                chunk = HEAD.Decoder(chunk_data)
            elif chunk_name == 'MATE':
                chunk = MATE.Decoder(self.parsed['header'])
            elif chunk_name == 'GEOM':
                chunk = GEOM.Decoder(self.parsed['header'])
            elif chunk_name == 'CAME':
                chunk = CAME.Decoder(self.parsed['header'])
            elif chunk_name == 'NODE':
                chunk = NODE.Decoder(self.parsed['header'])
            elif chunk_name == 'WEND':
                chunk = WEND.Decoder(self.parsed['header'])
            else:
                raise TypeError(f'Unknown chunk: {chunk_name}')

            chunk.parse(chunk_data)

            if chunk_name == 'HEAD':
                self.parsed['header'] = chunk.parsed
            elif chunk_name == 'MATE':
                self.parsed['materials'].append(chunk.parsed)
            elif chunk_name == 'GEOM':
                self.parsed['geometries'].append(chunk.parsed)
            elif chunk_name == 'CAME':
                self.parsed['cameras'].append(chunk.parsed)
            elif chunk_name == 'NODE':
                self.parsed['nodes'] = chunk.parsed


class Writer:
    def __init__(self, data: dict):
        self.writen = b'SC3D'

        head = HEAD.Encoder()
        head.encode(data['header'])

        self.write_chunk(head)

        # TODO: make materials
        for material in data['materials']:
            mate = MATE.Encoder()
            mate.encode(material)

            self.write_chunk(mate)

        for geometry in data['geometries']:
            geom = GEOM.Encoder()
            geom.encode(geometry)

            self.write_chunk(geom)

        # TODO: make cameras
        for camera in data['cameras']:
            came = CAME.Encoder()
            came.encode(camera)

            self.write_chunk(came)

        node = NODE.Encoder()
        node.encode(data['nodes'])
        self.write_chunk(node)

        wend = WEND.Encoder()
        self.write_chunk(wend)

    def write_chunk(self, chunk):
        self.writen += chunk.length.to_bytes(4, 'big') + chunk.chunk_name.encode('utf-8') + chunk.buffer
        self.writen += binascii.crc32(chunk.name.encode('utf-8') + chunk.buffer).to_bytes(4, 'big')
