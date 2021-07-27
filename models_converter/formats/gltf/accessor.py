from .gltf_property import GlTFProperty


class Accessor(GlTFProperty):
    class Sparse(GlTFProperty):
        class Indices(GlTFProperty):
            def __init__(self):
                super().__init__()
                self.buffer_view = None
                self.component_type = None

                self.byte_offset = 0

        class Values(GlTFProperty):
            def __init__(self):
                super().__init__()
                self.buffer_view = None

                self.byte_offset = 0

        def __init__(self):
            super().__init__()
            self.count = None
            self.indices = self.Indices()
            self.values = self.Values()

    def __init__(self):
        super().__init__()
        self.component_type = None
        self.count = None
        self.type = None

        self.buffer_view = None
        self.byte_offset = 0
        self.normalized = False
        self.max = None
        self.min = None
        self.sparse = self.Sparse()
        self.name = None
