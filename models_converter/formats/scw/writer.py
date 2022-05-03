import binascii

from .chunks import *
from ..universal import Scene
from ...interfaces import WriterInterface


class Writer(WriterInterface):
    MAGIC = b'SC3D'

    def __init__(self):
        self.writen = self.MAGIC

    def write(self, scene: Scene):
        head = HEAD()
        head.version = 2
        head.frame_rate = 30
        head.first_frame = 0
        head.last_frame = 0
        head.materials_file = 'sc3d/character_materials.scw' if len(scene.get_geometries()) > 0 else None

        self._write_chunk(head)

        # TODO: materials
        for material in scene.get_materials():
            mate = MATE(head)

            self._write_chunk(mate)

        for geometry in scene.get_geometries():
            geom = GEOM(head)
            geom.geometry = geometry

            self._write_chunk(geom)

        for camera in scene.get_cameras():
            came = CAME(head)
            came.camera = camera

            self._write_chunk(came)

        node = NODE(head)
        node.nodes = scene.get_nodes()

        self._write_chunk(node)

        wend = WEND()

        self._write_chunk(wend)

    def _write_chunk(self, chunk: Chunk):
        chunk.encode()

        self.writen += chunk.length.to_bytes(4, 'big') + chunk.chunk_name.encode('utf-8') + chunk.buffer
        self.writen += binascii.crc32(chunk.chunk_name.encode('utf-8') + chunk.buffer).to_bytes(4, 'big')
