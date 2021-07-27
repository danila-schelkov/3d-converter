from .gltf_property import GlTFProperty


class Material(GlTFProperty):
    class NormalTextureInfo(GlTFProperty):
        def __init__(self):
            super().__init__()
            self.index = None

            self.tex_coord = None  # Default: 0
            self.scale = None  # Default: 1

    class OcclusionTextureInfo(GlTFProperty):
        def __init__(self):
            super().__init__()
            self.index = None

            self.tex_coord = None  # Default: 0
            self.strength = None  # Default: 1

    class PbrMetallicRoughness(GlTFProperty):
        def __init__(self):
            super().__init__()
            self.base_color_factor = None  # Default: [1, 1, 1, 1]
            self.base_color_texture = None
            self.metallic_factor = None  # Default: 1
            self.roughness_factor = None  # Default: 1
            self.metallic_roughness_texture = None

    def __init__(self):
        super().__init__()
        self.name = None
        self.pbr_metallic_roughness = None
        self.normal_texture = None
        self.occlusion_texture = None
        self.emissive_texture = None
        self.emissive_factor = None  # Default: [0, 0, 0]
        self.alpha_mode = None  # Default: 'OPAQUE'
        self.alpha_cutoff = None  # Default: 0.5
        self.double_sided = None  # Default: False
