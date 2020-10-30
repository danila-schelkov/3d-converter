import binascii

from .chunks import *


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
