from .gltf_property import GlTFProperty
from . import *


class GlTF(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.asset = Asset()

        self.extensions_used = None
        self.extensions_required = None

        self.accessors = Accessor()
        self.animations = Animation()
        self.buffers = Buffer()
        self.buffer_views = BufferView()
        self.cameras = Camera()
        self.images = Image()
        self.materials = Material()
        self.meshes = Mesh()
        self.nodes = Node()
        self.samplers = Sampler()
        self.scene = None
        self.scenes = Scene()
        self.skins = Skin()
        self.textures = Texture()
