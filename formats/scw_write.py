import binascii

from chunks import *


def _(*args):
    print('[ScwUtils]', end=' ')
    for arg in args:
        print(arg, end=' ')
    print()


class Writer:
    def __init__(self, data: dict):
        self.writen = b'SC3D'

        head = HEAD.Encoder(data['header'])

        self.write_chunk(head)

        # TODO: make materials
        for material in data['materials']:
            mate = MATE.Encoder(material)

            self.write_chunk(mate)

        for geometry in data['geometries']:
            geom = GEOM.Encoder(geometry)

            self.write_chunk(geom)

        # TODO: make cameras
        for camera in data['cameras']:
            came = CAME.Encoder(camera)

            self.write_chunk(came)

        node = NODE.Encoder(data['nodes'])
        self.write_chunk(node)

        wend = WEND.Encoder()
        self.write_chunk(wend)

    def write_chunk(self, chunk):
        self.writen += chunk.length.to_bytes(4, 'big') + chunk.name.encode('utf-8') + chunk.buffer
        self.writen += binascii.crc32(chunk.name.encode('utf-8') + chunk.buffer).to_bytes(4, 'big')
