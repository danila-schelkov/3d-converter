import binascii

from chunks import HEAD, GEOM, NODE
from chunks import WEND


def _(*args):
    print('[ScwUtils]', end=' ')
    for arg in args:
        print(arg, end=' ')
    print()


class Writer:
    def __init__(self, info: dict):
        self.writen = b'SC3D'

        head = HEAD.Encoder(info['header'])

        self.write_chunk(head)

        # TODO: make materials
        # for material in info['materials']:
        #     mate = MATE.Encoder(material)
        #
        #     self.write_chunk(mate)

        for geometry in info['geometries']:
            geom = GEOM.Encoder(geometry)

            self.write_chunk(geom)

        # TODO: make cameras
        # for camera in info['cameras']:
        #     came = CAME.Encoder(camera)
        #
        #     self.write_chunk(came)

        node = NODE.Encoder(info['nodes'])
        self.write_chunk(node)

        wend = WEND.Encoder()
        self.write_chunk(wend)

    def write_chunk(self, chunk):
        self.writen += chunk.length.to_bytes(4, 'big') + chunk.name.encode('utf-8') + chunk.buffer
        self.writen += binascii.crc32(chunk.name.encode('utf-8') + chunk.buffer).to_bytes(4, 'big')

# info: dict - template
# {'header': {'version': 2,
#             'materials_file': 'sc3d/character_materials.scw'},
#  'materials': [{
#      'name': ...,
#      'effect': {
#          'ambient': ,
#          'diffuse': ,
#          'specular': ,
#          'colorize': ,
#          'emission': ,
#          'lightmaps': {
#              'diffuse': ,
#              'specular':
#          },
#          'tint':
#      }
#  }],
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
