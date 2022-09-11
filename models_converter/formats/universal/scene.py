from typing import List

from models_converter.formats.universal.camera import Camera
from models_converter.formats.universal.geometry import Geometry
from models_converter.formats.universal.node import Node


class Scene:
    def __init__(self):
        self._frame_rate: int = 30

        self._materials = []
        self._geometries = []
        self._cameras = []
        self._nodes = []

    def get_materials(self) -> List:
        return self._materials

    def add_material(self, material):
        self._materials.append(material)

    def get_geometries(self) -> List[Geometry]:
        return self._geometries

    def add_geometry(self, geometry: Geometry):
        self._geometries.append(geometry)

    def get_cameras(self) -> List[Camera]:
        return self._cameras

    def add_camera(self, camera: Camera):
        self._cameras.append(camera)

    def get_nodes(self) -> List[Node]:
        return self._nodes

    def add_node(self, node: Node):
        self._nodes.append(node)

    def import_nodes(self, animation_scene):
        for node in self._nodes:
            for animation_node in animation_scene.get_nodes():
                if node.get_name() == animation_node.get_name():
                    node.set_frames(animation_node.get_frames())
                    break

    def get_frame_rate(self) -> int:
        return self._frame_rate

    def set_frame_rate(self, frame_rate: int):
        self._frame_rate = frame_rate
