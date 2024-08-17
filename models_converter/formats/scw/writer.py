import binascii

from .chunks import *
from ..universal import Scene
from ...interfaces import WriterInterface


def _create_default_header(scene) -> HEAD:
    head = HEAD()
    head.version = 2
    head.frame_rate = 30
    head.first_frame = 0
    head.last_frame = 0
    head.materials_file = (
        "sc3d/character_materials.scw" if len(scene.get_geometries()) > 0 else None
    )

    return head


class Writer(WriterInterface):
    MAGIC = b"SC3D"

    def __init__(self):
        self.writen = self.MAGIC

    def write(self, scene: Scene) -> None:
        head = _create_default_header(scene)

        self._write_chunk(head, None)

        # TODO: materials
        for material in scene.get_materials():
            self._write_chunk(MATE(material), head)

        for geometry in scene.get_geometries():
            self._write_chunk(GEOM(geometry), head)

        for camera in scene.get_cameras():
            self._write_chunk(CAME(camera), head)

        self._write_chunk(NODE(scene.get_nodes()), head)
        self._write_chunk(WEND(), head)

    def _write_chunk(self, chunk: Chunk, head: HEAD | None):
        chunk.encode(head)

        self.writen += (
            chunk.length.to_bytes(4, "big")
            + chunk.chunk_name.encode("utf-8")
            + chunk.buffer
        )
        self.writen += binascii.crc32(
            chunk.chunk_name.encode("utf-8") + chunk.buffer
        ).to_bytes(4, "big")
