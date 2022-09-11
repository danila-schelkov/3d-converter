from typing import List

from models_converter.utilities.math import Quaternion
from models_converter.utilities.math import Vector3


class Node:
    class Instance:
        class Bind:
            def __init__(self, symbol: str = None, target: str = None):
                self._symbol = symbol
                self._target = target

            def get_symbol(self) -> str or None:
                return self._symbol

            def get_target(self) -> str or None:
                return self._target

        def __init__(self, *, name: str, instance_type: str):
            self._name: str = name
            self._type: str = instance_type
            self._target: str or None = None
            self._binds = []

        def __repr__(self) -> str:
            return f'{self._name} - {self._type}'

        def get_name(self) -> str:
            return self._name

        def get_type(self) -> str:
            return self._type

        def get_target(self) -> str:
            return self._target

        def set_target(self, target: str):
            self._target = target

        def get_binds(self) -> list:
            return self._binds

        def add_bind(self, symbol: str, target: str):
            self._binds.append(Node.Instance.Bind(symbol, target))

    class Frame:
        def __init__(self, frame_id: int, position: Vector3 = None, scale: Vector3 = None, rotation: Quaternion = None):
            self._id: int = frame_id
            self._position: Vector3 = position
            self._scale: Vector3 = scale
            self._rotation: Quaternion = rotation

        def get_id(self) -> int:
            return self._id

        def get_rotation(self) -> Quaternion:
            return self._rotation

        def set_rotation(self, rotation: Quaternion):
            self._rotation = rotation

        def get_position(self) -> Vector3:
            return self._position

        def set_position(self, position: Vector3):
            self._position = position

        def get_scale(self) -> Vector3:
            return self._scale

        def set_scale(self, scale: Vector3):
            self._scale = scale

    def __init__(self, *, name: str, parent: str):
        self.frames_settings = 0

        self._name: str = name
        self._parent: str or None = parent
        self._instances = []
        self._frames = []

    def __repr__(self) -> str:
        result = self._name
        if self._parent:
            result += " <- " + self._parent

        return f'Node({result})'

    def get_name(self) -> str:
        return self._name

    def get_parent(self) -> str or None:
        return self._parent

    def get_instances(self) -> List[Instance]:
        return self._instances

    def add_instance(self, instance: Instance):
        self._instances.append(instance)

    def get_frames(self) -> List[Frame]:
        return self._frames

    def add_frame(self, frame: Frame):
        self._frames.append(frame)

    def set_frames(self, frames: List[Frame]):
        self._frames.clear()

        for frame in frames:
            self._frames.append(frame)
