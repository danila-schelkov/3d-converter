from .gltf_property import GlTFProperty


class Node(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.camera = None
        self.children = None
        self.skin = None
        self.matrix = None  # Default: [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        self.mesh = None
        self.rotation = None  # Default: [0, 0, 0, 1]
        self.scale = None  # Default: [1, 1, 1]
        self.translation = None  # Default: [0, 0, 0]
        self.weights = None
        self.name = None
