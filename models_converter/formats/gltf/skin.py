from .gltf_property import GlTFProperty


class Skin(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.joints = None

        self.inverse_bind_matrices = None
        self.skeleton = None
        self.name = None
