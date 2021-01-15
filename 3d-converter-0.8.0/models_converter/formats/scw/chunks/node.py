from . import Chunk


class NODE(Chunk):
    def __init__(self, header: dict):
        super().__init__(header)
        self.chunk_name = 'NODE'

    def parse(self, buffer: bytes):
        super().parse(buffer)
        nodes = []

        nodes_count = self.readUShort()
        for node in range(nodes_count):
            node_data = {
                'name': self.readString(),
                'parent': self.readString()
            }

            instances_count = self.readUShort()
            node_data['instances'] = [{}] * instances_count
            for x in range(instances_count):
                instance_type = self.readChar(4)
                instance_name = self.readString()

                node_data['instances'][x] = {}
                if instance_type in ['GEOM', 'CONT']:
                    materials_count = self.readUShort()
                    binds = []
                    for bind in range(materials_count):
                        binds.append({})
                        symbol = self.readString()
                        target = self.readString()
                        binds[bind] = {'symbol': symbol,
                                       'target': target}
                    node_data['instances'][x]['binds'] = binds
                elif instance_type in ['CAME']:
                    target = self.readString()
                    node_data['instances'][x]['target'] = target
                node_data['instances'][x]['instance_name'] = instance_name
                node_data['instances'][x]['instance_type'] = instance_type

            frames_count = self.readUShort()
            node_data['frames'] = []
            if frames_count > 0:
                rotation = {'x': 0, 'y': 0, 'z': 0, 'w': 0}
                scale_x, scale_y, scale_z = 0, 0, 0
                pos_x, pos_y, pos_z = 0, 0, 0

                settings = list(bin(self.readUByte())[2:].zfill(8))
                settings = [bool(int(value)) for value in settings]
                node_data['frames_settings'] = settings
                for frame in range(frames_count):
                    frame_data = {
                        'frame_id': self.readUShort()
                    }

                    if settings[7] or frame == 0:  # Rotation
                        rotation = {
                            'x': self.readNShort(),
                            'y': self.readNShort(),
                            'z': self.readNShort(),
                            'w': self.readNShort()
                        }

                    if settings[4] or frame == 0:  # Position X
                        pos_x = self.readFloat()
                    if settings[5] or frame == 0:  # Position Y
                        pos_y = self.readFloat()
                    if settings[6] or frame == 0:  # Position Z
                        pos_z = self.readFloat()

                    if settings[1] or frame == 0:  # Scale X
                        scale_x = self.readFloat()
                    if settings[2] or frame == 0:  # Scale Y
                        scale_y = self.readFloat()
                    if settings[3] or frame == 0:  # Scale Z
                        scale_z = self.readFloat()

                    frame_data['rotation'] = rotation
                    frame_data['position'] = {
                        'x': pos_x,
                        'y': pos_y,
                        'z': pos_z
                    }
                    frame_data['scale'] = {
                        'x': scale_x,
                        'y': scale_y,
                        'z': scale_z
                    }

                    node_data['frames'].append(frame_data)
            nodes.append(node_data)
        setattr(self, 'nodes', nodes)

    def encode(self):
        super().encode()

        self.writeUShort(len(self.get('nodes')))
        for node in self.get('nodes'):
            self.writeString(node['name'])
            self.writeString(node['parent'])

            self.writeUShort(len(node['instances']))
            for instance in node['instances']:
                self.writeChar(instance['instance_type'])
                self.writeString(instance['instance_name'])
                self.writeUShort(len(instance['binds']))
                for bind in instance['binds']:
                    self.writeString(bind['symbol'])
                    self.writeString(bind['target'])

            if 'frames_settings' in node:
                frames_settings = node['frames_settings']
            else:
                frames_settings = None
            self.encode_frames(node['frames'], frames_settings)

        self.length = len(self.buffer)

    def encode_frames(self, frames, frames_settings):
        self.writeUShort(len(frames))
        if len(frames) > 0:
            self.writeUByte(int(''.join([('1' if item else '0') for item in frames_settings])[::], 2))
            for frame in frames:
                self.writeUShort(frame['frame_id'])
                if frames_settings[7] or frames.index(frame) == 0:  # Rotation
                    self.writeNShort(frame['rotation']['x'])
                    self.writeNShort(frame['rotation']['y'])
                    self.writeNShort(frame['rotation']['z'])
                    self.writeNShort(frame['rotation']['w'])

                if frames_settings[4] or frames.index(frame) == 0:  # Position X
                    self.writeFloat(frame['position']['x'])
                if frames_settings[5] or frames.index(frame) == 0:  # Position Y
                    self.writeFloat(frame['position']['y'])
                if frames_settings[6] or frames.index(frame) == 0:  # Position Z
                    self.writeFloat(frame['position']['z'])

                if frames_settings[1] or frames.index(frame) == 0:  # Scale X
                    self.writeFloat(frame['scale']['x'])
                if frames_settings[2] or frames.index(frame) == 0:  # Scale Y
                    self.writeFloat(frame['scale']['y'])
                if frames_settings[3] or frames.index(frame) == 0:  # Scale Z
                    self.writeFloat(frame['scale']['z'])
