import binascii

from scw.chunks import HEAD, MATE, GEOM, CAME, NODE


def _(*args):
    print('[ScwUtils]', end=' ')
    for arg in args:
        print(arg, end=' ')
    print()


class Writer:
    def __init__(self, info: dict):
        self.writed = b'SC3D'

        head = HEAD.Encoder(info['header'])

        self.writed += len(head.buffer).to_bytes(4, 'big') + b'HEAD' + head.buffer
        self.writed += binascii.crc32(b'HEAD' + head.buffer).to_bytes(4, 'big')

        # TODO: make materials
        # for material in info['materials']:
        #     mate = MATE.Encoder(material)
        #
        #     self.writed += len(mate.buffer).to_bytes(4, 'big') + b'MATE' + mate.buffer
        #     self.writed += binascii.crc32(b'MATE' + mate.buffer).to_bytes(4, 'big')

        for geometry in info['geometries']:
            geom = GEOM.Encoder(geometry)

            self.writed += len(geom.buffer).to_bytes(4, 'big') + b'GEOM' + geom.buffer
            self.writed += binascii.crc32(b'GEOM' + geom.buffer).to_bytes(4, 'big')

        # TODO: make cameras
        # for camera in info['cameras']:
        #     came = CAME.Encoder(camera)
        #
        #     self.writed += len(came.buffer).to_bytes(4, 'big') + b'CAME' + came.buffer
        #     self.writed += binascii.crc32(b'CAME' + came.buffer).to_bytes(4, 'big')

        node = NODE.Encoder(info['nodes'])

        self.writed += len(node.buffer).to_bytes(4, 'big') + b'NODE' + node.buffer
        self.writed += binascii.crc32(b'NODE' + node.buffer).to_bytes(4, 'big')

        self.writed += (0).to_bytes(4, 'big') + b'WEND' + binascii.crc32(b'WEND').to_bytes(4, 'big')


# info: dict - template
# {'header': {'version': 2,
#             'materials_file': 'sc3d/character_materials.scw'},
 'materials': [{
     'name': ...,
     ''
 }],
#  'geometries': [{...}],
#  'cameras': [{...}],
#  'nodes': [{'name': ...,
#             'parent': ...,
#             'has_target': False,
#             'frames': [{'frame_id': 0,
#                         'rotation': {'x': ...,
#                                      'y': ...,
#                                      'z': ...,
#                                      'w': ...},
#                         'position': {'x': ...,
#                                      'y': ...,
#                                      'z': ...},
#                         'scale': {'x': ...,
#                                   'y': ...,
#                                   'z': ...},
#                         }]}]}
