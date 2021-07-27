from .gltf_property import GlTFProperty


class BufferView(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.buffer = None
        self.byte_length = None

        self.byte_offset = 0
        self.byte_stride = None
        self.target = None
        self.name = None
