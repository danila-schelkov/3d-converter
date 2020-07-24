import json

from chunks import *
from utils.reader import Reader


def _(*args):
    print('[ScwUtils]', end=' ')
    for arg in args:
        print(arg, end=' ')
    print()


class Parser(Reader):
    def __init__(self, file_data: bytes):
        super().__init__(file_data)
        self.file_data = file_data
        self.readed = {
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
        for chunk in self.chunks:
            chunk_name = chunk['name']
            chunk_data = chunk['data']

            if chunk_name == 'HEAD':
                head = HEAD.Decoder(chunk_data)
                self.readed['header'] = head.readed
            elif chunk_name == 'MATE':
                mate = MATE.Decoder(chunk_data, self.readed['header'])
                self.readed['materials'].append(mate.readed)
            elif chunk_name == 'GEOM':
                geom = GEOM.Decoder(chunk_data, self.readed['header'])
                self.readed['geometries'].append(geom.readed)
            elif chunk_name == 'CAME':
                came = CAME.Decoder(chunk_data, self.readed['header'])
                self.readed['cameras'].append(came.readed)
            elif chunk_name == 'NODE':
                node = NODE.Decoder(chunk_data, self.readed['header'])
                self.readed['nodes'] = node.readed
            elif chunk_name == 'WEND':
                WEND.Decoder(chunk_data)
            else:
                raise TypeError(f'Unknown chunk: {chunk_name}')


if __name__ == '__main__':
    with open('../8bit_geo.scw', 'rb') as file:
        parser = Parser(file.read())
        parser.split_chunks()
        parser.parse()

        json.dump(parser.readed, open('../parsed_info.json', 'w'))

        file.close()
