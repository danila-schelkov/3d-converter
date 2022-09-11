from .gltf_property import GlTFProperty


class Mesh(GlTFProperty):
    class Primitive(GlTFProperty):
        def __init__(self):
            super().__init__()
            self.attributes = None

            self.indices = None
            self.material = None
            self.mode = None  # Default: 4
            self.targets = None

    def __init__(self):
        super().__init__()
        self.primitives = self.Primitive

        self.weights = None
        self.name = None
