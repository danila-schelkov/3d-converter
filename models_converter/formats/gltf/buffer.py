from .gltf_property import GlTFProperty


class Buffer(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.byte_length = None

        self.uri = None
        self.name = None
