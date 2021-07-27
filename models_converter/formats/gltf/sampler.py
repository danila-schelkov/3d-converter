from .gltf_property import GlTFProperty


class Sampler(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.mag_filter = None
        self.min_filter = None
        self.wrap_s = None  # Default: 10497
        self.wrap_t = None  # Default: 10497
        self.name = None
