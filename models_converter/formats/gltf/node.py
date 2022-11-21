from .gltf_property import GlTFProperty
from ...utilities.math import Vector3, Quaternion
from ...utilities.matrix.matrix4x4 import Matrix4x4


class Node(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.camera = None
        self.children = None
        self.skin = None
        self.matrix = Matrix4x4()
        self.mesh = None
        self.rotation = Quaternion()  # Default: [0, 0, 0, 1]
        self.scale = Vector3(1, 1, 1)  # Default: [1, 1, 1]
        self.translation = Vector3()  # Default: [0, 0, 0]
        self.weights = None
        self.name = None
