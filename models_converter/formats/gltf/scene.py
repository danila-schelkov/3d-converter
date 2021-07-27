from .gltf_property import GlTFProperty


class Scene(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.nodes = None
        self.name = None
