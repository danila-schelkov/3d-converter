from .gltf_property import GlTFProperty


class Asset(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.version = None

        self.copyright = None
        self.generator = None
        self.min_version = None
