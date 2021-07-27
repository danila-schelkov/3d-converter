from .gltf_property import GlTFProperty


class Camera(GlTFProperty):
    class Orthographic(GlTFProperty):
        def __init__(self):
            super().__init__()
            self.xmag = None
            self.ymag = None
            self.zfar = None
            self.znear = None

    class Perspective(GlTFProperty):
        def __init__(self):
            super().__init__()
            self.yfov = None
            self.znear = None

            self.aspect_ratio = None
            self.zfar = None

    def __init__(self):
        super().__init__()
        self.type = None

        self.orthographic = None
        self.perspective = None
        self.name = None
