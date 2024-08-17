from typing import cast

from models_converter.utilities.math import Vector3
from models_converter.utilities.math import Quaternion
from . import Chunk
from ...universal.node import Node


class NODE(Chunk):
    chunk_name = "NODE"

    def __init__(self, nodes: list[Node] | None = None):
        if nodes is None:
            nodes = []

        self.nodes: list[Node] = nodes

    def parse(self, buffer: bytes, *args) -> None:
        super().parse(buffer)

        nodes_count = self.read_unsigned_int16()
        for node_index in range(nodes_count):
            node = Node(name=cast(str, self.read_string()), parent=self.read_string())

            instances_count = self.read_unsigned_int16()
            for x in range(instances_count):
                instance_type = self.read(4).decode()
                name = self.read_string()

                instance = Node.Instance(
                    name=cast(str, name), instance_type=cast(str, instance_type)
                )

                if instance.get_type() in ("GEOM", "CONT"):
                    materials_count = self.read_unsigned_int16()
                    for bind in range(materials_count):
                        symbol = self.read_string()
                        target = self.read_string()
                        assert symbol is not None
                        assert target is not None
                        instance.add_bind(symbol, target)
                elif instance.get_type() == "CAME":
                    instance.set_target(self.read_string())
                node.add_instance(instance)

            frames_count = self.read_unsigned_int16()
            if frames_count > 0:
                rotation = Quaternion()
                position = Vector3()
                scale = Vector3()

                node.frames_settings = self.read_unsigned_int8()
                for frame_index in range(frames_count):
                    frame = Node.Frame(self.read_unsigned_int16())

                    if node.frames_settings & 1 or frame_index == 0:  # Rotation
                        rotation.x = self.read_normalized_int16()
                        rotation.y = self.read_normalized_int16()
                        rotation.z = self.read_normalized_int16()
                        rotation.w = self.read_normalized_int16()

                    if node.frames_settings & 2 or frame_index == 0:  # Position X
                        position.x = self.read_float()
                    if node.frames_settings & 4 or frame_index == 0:  # Position Y
                        position.y = self.read_float()
                    if node.frames_settings & 8 or frame_index == 0:  # Position Z
                        position.z = self.read_float()

                    if node.frames_settings & 16 or frame_index == 0:  # Scale X
                        scale.x = self.read_float()
                    if node.frames_settings & 32 or frame_index == 0:  # Scale Y
                        scale.y = self.read_float()
                    if node.frames_settings & 64 or frame_index == 0:  # Scale Z
                        scale.z = self.read_float()

                    frame.set_rotation(rotation.clone())
                    frame.set_position(position.clone())
                    frame.set_scale(scale.clone())

                    node.add_frame(frame)
            self.nodes.append(node)

    def encode(self, *args) -> None:
        super().encode()

        self.write_unsigned_int16(len(self.nodes))
        for node in self.nodes:
            self.write_string(node.get_name())
            self.write_string(node.get_parent())

            self.write_unsigned_int16(len(node.get_instances()))
            for instance in node.get_instances():
                self.write(instance.get_type().encode())
                self.write_string(instance.get_name())
                self.write_unsigned_int16(len(instance.get_binds()))
                for bind in instance.get_binds():
                    self.write_string(bind.get_symbol())
                    self.write_string(bind.get_target())

            self._encode_frames(node.get_frames(), node.frames_settings)

        self.length = len(self.buffer)

    def _encode_frames(self, frames, frames_settings):
        self.write_unsigned_int16(len(frames))
        if len(frames) > 0:
            self.write_unsigned_int8(frames_settings)
            for frame in frames:
                self.write_unsigned_int16(frame.get_id())
                if frames_settings & 128 or frames.index(frame) == 0:  # Rotation
                    rotation = frame.get_rotation()

                    self.write_normalized_int16(rotation.x)
                    self.write_normalized_int16(rotation.y)
                    self.write_normalized_int16(rotation.z)
                    self.write_normalized_int16(rotation.w)

                if frames_settings & 16 or frames.index(frame) == 0:  # Position X
                    self.write_float(frame.get_position().x)
                if frames_settings & 32 or frames.index(frame) == 0:  # Position Y
                    self.write_float(frame.get_position().y)
                if frames_settings & 64 or frames.index(frame) == 0:  # Position Z
                    self.write_float(frame.get_position().z)

                if frames_settings & 2 or frames.index(frame) == 0:  # Scale X
                    self.write_float(frame.get_scale().x)
                if frames_settings & 4 or frames.index(frame) == 0:  # Scale Y
                    self.write_float(frame.get_scale().y)
                if frames_settings & 8 or frames.index(frame) == 0:  # Scale Z
                    self.write_float(frame.get_scale().z)
