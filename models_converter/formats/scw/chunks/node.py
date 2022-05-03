from models_converter.utilities.math import Vector3
from models_converter.utilities.math import Quaternion
from . import Chunk
from ...universal.node import Node


class NODE(Chunk):
    def __init__(self, header):
        super().__init__(header)
        self.chunk_name = 'NODE'

        self.nodes = []

    def parse(self, buffer: bytes):
        super().parse(buffer)

        nodes_count = self.readUShort()
        for node_index in range(nodes_count):
            node = Node(
                name=self.readString(),
                parent=self.readString()
            )

            instances_count = self.readUShort()
            for x in range(instances_count):
                instance = Node.Instance(
                    instance_type=self.readChars(4),
                    name=self.readString()
                )

                if instance.get_type() in ('GEOM', 'CONT'):
                    materials_count = self.readUShort()
                    for bind in range(materials_count):
                        symbol = self.readString()
                        target = self.readString()
                        instance.add_bind(symbol, target)
                elif instance.get_type() == 'CAME':
                    instance.set_target(self.readString())
                node.add_instance(instance)

            frames_count = self.readUShort()
            if frames_count > 0:
                rotation = Quaternion()
                position = Vector3()
                scale = Vector3()

                node.frames_settings = self.readUByte()
                for frame_index in range(frames_count):
                    frame = Node.Frame(self.readUShort())

                    if node.frames_settings & 1 or frame_index == 0:  # Rotation
                        rotation.x = self.readNShort()
                        rotation.y = self.readNShort()
                        rotation.z = self.readNShort()
                        rotation.w = self.readNShort()

                    if node.frames_settings & 2 or frame_index == 0:  # Position X
                        position.x = self.readFloat()
                    if node.frames_settings & 4 or frame_index == 0:  # Position Y
                        position.y = self.readFloat()
                    if node.frames_settings & 8 or frame_index == 0:  # Position Z
                        position.z = self.readFloat()

                    if node.frames_settings & 16 or frame_index == 0:  # Scale X
                        scale.x = self.readFloat()
                    if node.frames_settings & 32 or frame_index == 0:  # Scale Y
                        scale.y = self.readFloat()
                    if node.frames_settings & 64 or frame_index == 0:  # Scale Z
                        scale.z = self.readFloat()

                    frame.set_rotation(rotation.clone())
                    frame.set_position(position.clone())
                    frame.set_scale(scale.clone())

                    node.add_frame(frame)
            self.nodes.append(node)

    def encode(self):
        super().encode()

        self.writeUShort(len(self.nodes))
        for node in self.nodes:
            self.writeString(node.get_name())
            self.writeString(node.get_parent())

            self.writeUShort(len(node.get_instances()))
            for instance in node.get_instances():
                self.writeChar(instance.get_type())
                self.writeString(instance.get_name())
                self.writeUShort(len(instance.get_binds()))
                for bind in instance.get_binds():
                    self.writeString(bind.get_symbol())
                    self.writeString(bind.get_target())

            self._encode_frames(node.get_frames(), node.frames_settings)

        self.length = len(self.buffer)

    def _encode_frames(self, frames, frames_settings):
        self.writeUShort(len(frames))
        if len(frames) > 0:
            self.writeUByte(frames_settings)
            for frame in frames:
                self.writeUShort(frame.get_id())
                if frames_settings & 128 or frames.index(frame) == 0:  # Rotation
                    rotation = frame.get_rotation()

                    self.writeNShort(rotation.x)
                    self.writeNShort(rotation.y)
                    self.writeNShort(rotation.z)
                    self.writeNShort(rotation.w)

                if frames_settings & 16 or frames.index(frame) == 0:  # Position X
                    self.writeFloat(frame.get_position().x)
                if frames_settings & 32 or frames.index(frame) == 0:  # Position Y
                    self.writeFloat(frame.get_position().y)
                if frames_settings & 64 or frames.index(frame) == 0:  # Position Z
                    self.writeFloat(frame.get_position().z)

                if frames_settings & 2 or frames.index(frame) == 0:  # Scale X
                    self.writeFloat(frame.get_scale().x)
                if frames_settings & 4 or frames.index(frame) == 0:  # Scale Y
                    self.writeFloat(frame.get_scale().y)
                if frames_settings & 8 or frames.index(frame) == 0:  # Scale Z
                    self.writeFloat(frame.get_scale().z)
