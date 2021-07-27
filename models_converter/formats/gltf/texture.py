from .gltf_property import GlTFProperty


class Texture(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.sampler = None
        self.source = None
        self.name = None
