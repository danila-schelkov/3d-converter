from models_converter.formats.gltf import GlTFProperty


class TextureInfo(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.index = None

        self.tex_coord = None  # Default: 0
