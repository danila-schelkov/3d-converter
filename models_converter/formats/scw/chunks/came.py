from typing import cast

from . import Chunk
from ...universal.camera import Camera


class CAME(Chunk):
    chunk_name = "CAME"

    def __init__(self, camera: Camera | None = None):
        self.camera: Camera | None = camera

    def parse(self, buffer: bytes, *args) -> None:
        super().parse(buffer)

        name = self.read_string()
        self.read_float()
        fov = self.read_float()
        aspect_ratio = self.read_float()
        near = self.read_float()
        far = self.read_float()

        self.camera = Camera(
            name=cast(str, name), fov=fov, aspect_ratio=aspect_ratio, near=near, far=far
        )

    def encode(self, header) -> None:
        super().encode()

        assert self.camera is not None

        self.write_string(self.camera.get_name())
        self.write_float(self.camera.get_v1())
        self.write_float(self.camera.get_fov())
        self.write_float(self.camera.get_aspect_ration())
        self.write_float(self.camera.get_near())
        self.write_float(self.camera.get_far())

        self.length = len(self.buffer)
