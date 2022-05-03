from . import Chunk
from ...universal.camera import Camera


class CAME(Chunk):
    def __init__(self, header):
        super().__init__(header)
        self.chunk_name = 'CAME'

        self.camera: Camera or None = None

    def parse(self, buffer: bytes):
        super().parse(buffer)

        name = self.readString()
        self.readFloat()
        fov = self.readFloat()
        aspect_ratio = self.readFloat()
        near = self.readFloat()
        far = self.readFloat()

        self.camera = Camera(name=name, fov=fov, aspect_ratio=aspect_ratio, near=near, far=far)

    def encode(self):
        super().encode()

        self.writeString(self.camera.get_name())
        self.writeFloat(self.camera.get_v1())
        self.writeFloat(self.camera.get_fov())
        self.writeFloat(self.camera.get_aspect_ration())
        self.writeFloat(self.camera.get_near())
        self.writeFloat(self.camera.get_far())

        self.length = len(self.buffer)
