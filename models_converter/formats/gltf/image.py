from .gltf_property import GlTFProperty


class Image(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.uri = None
        self.mime_type = None
        self.buffer_view = None
        self.name = None
