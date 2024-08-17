from models_converter.utilities.math import Quaternion
from models_converter.utilities.math import Vector3


class Node:
    class Instance:
        class Bind:
            def __init__(self, symbol: str | None = None, target: str | None = None):
                self._symbol = symbol
                self._target = target

            def get_symbol(self) -> str | None:
                return self._symbol

            def get_target(self) -> str | None:
                return self._target

        def __init__(self, *, name: str, instance_type: str):
            self._name: str = name
            self._type: str = instance_type
            self._target: str | None = None
            self._binds = []

        def __repr__(self) -> str:
            return f"{self._name} - {self._type}"

        def get_name(self) -> str:
            return self._name

        def set_name(self, name: str):
            self._name = name

        def get_type(self) -> str:
            return self._type

        def get_target(self) -> str | None:
            return self._target

        def set_target(self, target: str | None):
            self._target = target

        def get_binds(self) -> list:
            return self._binds

        def add_bind(self, symbol: str, target: str):
            self._binds.append(Node.Instance.Bind(symbol, target))

    class Frame:
        def __init__(
            self,
            frame_id: int,
            position: Vector3 | None = None,
            scale: Vector3 | None = None,
            rotation: Quaternion | None = None,
        ):
            self._id: int = frame_id
            self._position: Vector3 | None = position
            self._scale: Vector3 | None = scale
            self._rotation: Quaternion | None = rotation

        def get_id(self) -> int:
            return self._id

        def get_rotation(self) -> Quaternion | None:
            return self._rotation

        def set_rotation(self, rotation: Quaternion | None):
            self._rotation = rotation

        def get_position(self) -> Vector3 | None:
            return self._position

        def set_position(self, position: Vector3 | None):
            self._position = position

        def get_scale(self) -> Vector3 | None:
            return self._scale

        def set_scale(self, scale: Vector3 | None):
            self._scale = scale

    def __init__(self, *, name: str, parent: str | None):
        self.frames_settings = 0

        self._name: str = name
        self._parent: str | None = parent
        self._instances: list[Node.Instance] = []
        self._frames: list[Node.Frame] = []

    def __repr__(self) -> str:
        result = self._name
        if self._parent:
            result += " <- " + self._parent

        return f"Node({result})"

    def get_name(self) -> str:
        return self._name

    def get_parent(self) -> str | None:
        return self._parent

    def get_instances(self) -> list[Instance]:
        return self._instances

    def add_instance(self, instance: Instance):
        self._instances.append(instance)

    def get_frames(self) -> list[Frame]:
        return self._frames

    def add_frame(self, frame: Frame):
        self._frames.append(frame)

    def set_frames(self, frames: list[Frame]):
        self._frames.clear()

        for frame in frames:
            self._frames.append(frame)
