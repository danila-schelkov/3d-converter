from ..utils.reader import Reader
from ..utils.writer import Writer
from .chunk import Chunk


class HEAD(Chunk, Writer, Reader):
    def __init__(self, header=None):
        super().__init__(header)
        self.chunk_name = 'HEAD'

    def parse(self, buffer: bytes):
        Reader.__init__(self, buffer)

        setattr(self, 'version', self.readUShort())
        setattr(self, 'frame_rate', self.readUShort())
        setattr(self, 'v1', self.readUShort())
        setattr(self, 'v2', self.readUShort())
        setattr(self, 'materials_file', self.readString())
        if self.get('version') == 2:
            setattr(self, 'v3', self.readUByte())

    def encode(self):
        Writer.__init__(self)

        self.writeUShort(2)  # getattr(self, 'version')
        self.writeUShort(getattr(self, 'frame_rate'))
        self.writeUShort(0)  # getattr(self, 'v1')
        self.writeUShort(249)  # getattr(self, 'v2')
        self.writeString(getattr(self, 'materials_file'))
        self.writeUByte(0)  # getattr(self, 'v3')

        self.length = len(self.buffer)


class MATE(Chunk, Writer, Reader):
    def __init__(self, header: dict):
        super().__init__(header)
        self.chunk_name = 'MATE'

    def parse(self, buffer: bytes):
        Reader.__init__(self, buffer)

        setattr(self, 'name', self.readString())
        setattr(self, 'shader', self.readString())
        setattr(self, 'v1', self.readUByte())

        effect = {}
        use_ambient_tex = self.readBool()
        if use_ambient_tex:
            ambient_tex = self.readString()
            effect['ambient'] = ambient_tex
        else:
            a = self.readUByte()
            r = self.readUByte()
            g = self.readUByte()
            b = self.readUByte()
            ambient_color = (r, g, b, a)
            effect['ambient'] = ambient_color

        use_diffuse_tex = self.readBool()
        if use_diffuse_tex:
            diffuse_tex = self.readString()
            effect['diffuse'] = diffuse_tex
        else:
            a = self.readUByte()
            r = self.readUByte()
            g = self.readUByte()
            b = self.readUByte()
            diffuse_color = (r, g, b, a)
            effect['diffuse'] = diffuse_color

        use_specular_tex = self.readBool()
        if use_specular_tex:
            specular_tex = self.readString()
            effect['specular'] = specular_tex
        else:
            a = self.readUByte()
            r = self.readUByte()
            g = self.readUByte()
            b = self.readUByte()
            specular_color = (r, g, b, a)
            effect['specular'] = specular_color

        setattr(self, 'v2', self.readString())
        setattr(self, 'v3', self.readString())

        use_colorize_tex = self.readBool()
        if use_colorize_tex:
            colorize_tex = self.readString()
            effect['colorize'] = colorize_tex
        else:
            a = self.readUByte()
            r = self.readUByte()
            g = self.readUByte()
            b = self.readUByte()
            colorize_color = (r, g, b, a)
            effect['colorize'] = colorize_color

        use_emission_tex = self.readBool()
        if use_emission_tex:
            emission_tex = self.readString()
            effect['emission'] = emission_tex
        else:
            a = self.readUByte()
            r = self.readUByte()
            g = self.readUByte()
            b = self.readUByte()
            emission_color = (r, g, b, a)
            effect['emission'] = emission_color

        setattr(self, 'v4', self.readString())
        setattr(self, 'v5', self.readFloat())
        setattr(self, 'v6', self.readFloat())

        effect['lightmaps'] = {
            'diffuse': self.readString(),
            'specular': self.readString()
        }

        a = self.readUByte()
        r = self.readUByte()
        g = self.readUByte()
        b = self.readUByte()
        effect['tint'] = (r, g, b, a)

        setattr(self, 'effect', effect)

    def encode(self):
        Writer.__init__(self)

        self.length = len(self.buffer)


class GEOM(Chunk, Writer, Reader):
    def __init__(self, header: dict):
        super().__init__(header)
        self.chunk_name = 'GEOM'

    def parse(self, buffer: bytes):
        Reader.__init__(self, buffer)

        setattr(self, 'name', self.readString())
        setattr(self, 'group', self.readString())
        if self.header['version'] < 2:
            matrix = []
            for x in range(4):
                temp_list = []
                for x1 in range(4):
                    temp_list.append(self.readFloat())
                matrix.append(temp_list)

        self.parse_vertices()
        self.parse_skin()
        self.parse_materials()

    def parse_vertices(self):
        vertices = []
        inputs = []

        vertex_count = self.readUByte()
        for x in range(vertex_count):
            vertex = []
            vertex_type = self.readString()
            vertex_index = self.readUByte()
            vertex_shorts = self.readUShort()
            vertex_scale = self.readFloat()
            vertex_count = self.readUInt32()

            if vertex_type == 'VERTEX':
                vertex_type = 'POSITION'

            for x1 in range(vertex_count):
                coordinates_massive = []
                for x2 in range(vertex_shorts):
                    coordinate = self.readShort()
                    coordinates_massive.append(coordinate / 32512)
                if vertex_type == 'TEXCOORD':
                    coordinates_massive[1::2] = [1 - x for x in coordinates_massive[1::2]]
                vertex.append(coordinates_massive)

            inputs.append({
                'type': vertex_type,
                'offset': x,
                'name': f'{vertex_type.lower()}_0'
            })

            vertices.append({
                'name': f'{vertex_type.lower()}_0',
                'type': vertex_type,
                'index': vertex_index,
                'scale': vertex_scale,
                'vertex': vertex
            })
        setattr(self, 'inputs', inputs)
        setattr(self, 'vertices', vertices)

    def parse_skin(self):
        bind_matrix = []

        setattr(self, 'have_bind_matrix', self.readBool())
        if getattr(self, 'have_bind_matrix'):
            for x in range(16):
                bind_matrix.append(self.readFloat())

        setattr(self, 'bind_matrix', bind_matrix)

        self.parse_joints()
        self.parse_weights()

    def parse_joints(self):
        joints = []

        joint_counts = self.readUByte()
        for x in range(joint_counts):
            joint_matrix = []
            joint_name = self.readString()
            for x1 in range(16):
                joint_matrix.append(self.readFloat())
            joints.append({'name': joint_name, 'matrix': joint_matrix})

        setattr(self, 'joints', joints)

    def parse_weights(self):
        vertex_weights = []
        weights = []
        vcount = []

        vertex_weights_count = self.readUInt32()
        for x in range(vertex_weights_count):
            vcount.append(0)
            joint_a = self.readUByte()
            joint_b = self.readUByte()
            joint_c = self.readUByte()
            joint_d = self.readUByte()
            weight_a = self.readUShort()
            weight_b = self.readUShort()
            weight_c = self.readUShort()
            weight_d = self.readUShort()
            temp_list = [
                [joint_a, weight_a],
                [joint_b, weight_b],
                [joint_c, weight_c],
                [joint_d, weight_d]
            ]
            for pair in temp_list:
                if pair[1] != 0:
                    vcount[x] += 1
                    vertex_weights.append(pair[0])
                    if pair[1] / 65535 not in weights:
                        weights.append(pair[1] / 65535)
                    vertex_weights.append(weights.index(pair[1] / 65535))

        setattr(self, 'weights',
                {
                    'vertex_weights': vertex_weights,
                    'weights': weights,
                    'vcount': vcount
                })

    def parse_materials(self):
        materials = []

        materials_count = self.readUByte()
        for x in range(materials_count):
            polygons = []
            material_name = self.readString()
            self.readString()
            polygons_count = self.readUShort()
            inputs_count = self.readUByte()
            vertex_id_length = self.readUByte()
            for x1 in range(polygons_count):
                temp_list = []
                for x2 in range(3):
                    second_temp_list = []
                    for x3 in range(inputs_count):
                        second_temp_list.append(self.readUInteger(vertex_id_length))
                    temp_list.append(second_temp_list)
                polygons.append(temp_list)
            materials.append({
                'name': material_name,
                'inputs': getattr(self, 'inputs'),
                'polygons': polygons
            })

        setattr(self, 'materials', materials)

    def encode(self):
        Writer.__init__(self)

        self.writeString(self.get('name'))
        self.writeString(self.get('group'))

        self.encode_vertices(self.get('vertices'))

        self.encode_skin()

        self.encode_materials()

        self.length = len(self.buffer)

    def encode_vertices(self, vertices: dict):
        self.writeUByte(len(vertices))
        for vertex in vertices:
            self.writeString(vertex['type'])
            self.writeUByte(vertex['index'])
            self.writeUShort(len(vertex['vertex'][0]))
            self.writeFloat(vertex['scale'])
            self.writeUInt32(len(vertex['vertex']))
            for coordinates_massive in vertex['vertex']:
                if vertex['type'] == 'TEXCOORD':
                    coordinates_massive[1::2] = [1 - x for x in coordinates_massive[1::2]]
                for coordinate in coordinates_massive:
                    # coordinate /= vertex['scale']
                    coordinate *= 32512
                    self.writeShort(round(coordinate))

    def encode_skin(self):
        self.writeBool(self.get('have_bind_matrix'))
        if self.get('have_bind_matrix'):
            for x in self.get('bind_matrix'):
                self.writeFloat(x)

        self.encode_joints()

        self.encode_weight()

    def encode_joints(self):
        if self.get('have_bind_matrix'):
            self.writeUByte(len(self.get('joints')))

            for joint in self.get('joints'):
                self.writeString(joint['name'])
                for x in joint['matrix']:
                    self.writeFloat(x)
        else:
            self.writeUByte(0)

    def encode_weight(self):
        if self.get('have_bind_matrix'):
            self.writeUInt32(len(self.get('weights')['vcount']))
            past_index = 0
            for vcount in self.get('weights')['vcount']:
                temp_list = []
                for x in range(vcount):
                    vertex_weights_index = x * 2 + past_index * 2
                    joint_id = self.get('weights')['vertex_weights'][vertex_weights_index]
                    weight_id = self.get('weights')['vertex_weights'][vertex_weights_index + 1]

                    weight = self.get('weights')['weights'][weight_id]

                    if weight > 1:
                        weight = 1
                    elif weight < 1:
                        weight = 0

                    weight = int(weight * 65535)
                    temp_list.append([joint_id, weight])
                past_index += vcount
                while len(temp_list) < 4:
                    temp_list.append([0, 0])
                for x in temp_list:
                    self.writeUByte(x[0])
                for x in temp_list:
                    self.writeUShort(x[1])
        else:
            self.writeUInt32(0)

    def encode_materials(self):
        self.writeUByte(len(self.get('materials')))
        for material in self.get('materials'):
            self.writeString(material['name'])
            self.writeString('')
            self.writeUShort(len(material['polygons']))

            # Calculate settings
            inputs_count = len(material['polygons'][0][0])

            maximal_value = 0
            for points in material['polygons']:
                for point in points:
                    for vertex in point:
                        if vertex > maximal_value:
                            maximal_value = vertex

            short_length = 1 if maximal_value <= 255 else 2

            # Write Settings
            self.writeUByte(inputs_count)
            self.writeUByte(short_length)

            # Write Polygons
            for points in material['polygons']:
                for point in points:
                    for vertex in point:
                        self.writeUInteger(vertex, short_length)


class CAME(Chunk, Writer, Reader):
    def __init__(self, header=None):
        super().__init__(header)
        self.chunk_name = 'CAME'

    def parse(self, buffer: bytes):
        super(Reader).__init__(buffer=buffer)

        setattr(self, 'name', self.readString())
        setattr(self, 'v1', self.readFloat())
        setattr(self, 'xFov', self.readFloat())
        setattr(self, 'aspectRatio', self.readFloat())
        setattr(self, 'zNear', self.readFloat())
        setattr(self, 'zFar', self.readFloat())

    def encode(self):
        Writer.__init__(self)

        self.writeString(getattr(self, 'name'))
        self.writeFloat(getattr(self, 'v1'))
        self.writeFloat(getattr(self, 'xFov'))
        self.writeFloat(getattr(self, 'aspectRatio'))
        self.writeFloat(getattr(self, 'zNear'))
        self.writeFloat(getattr(self, 'zFar'))

        self.length = len(self.buffer)


class NODE(Chunk, Writer, Reader):
    def __init__(self, header: dict):
        super().__init__(header)
        self.chunk_name = 'NODE'

    def parse(self, buffer: bytes):
        Reader.__init__(self, buffer)
        nodes = []

        nodes_count = self.readUShort()
        for node in range(nodes_count):
            node_data = {}

            node_data['name'] = self.readString()
            node_data['parent'] = self.readString()

            has_target = True if self.readUShort() else False
            node_data['has_target'] = has_target
            if has_target:
                target_type = self.readChar(4)
                target_name = self.readString()
                binds_count = self.readUShort()
                binds = []
                for bind in range(binds_count):
                    binds.append({})
                    symbol = self.readString()
                    target = self.readString()
                    binds[bind] = {'symbol': symbol,
                                   'target': target}
                node_data['target_type'] = target_type
                node_data['target'] = target_name
                node_data['binds'] = binds

            frames_count = self.readUShort()
            node_data['frames'] = []
            if frames_count > 0:
                settings = list(bin(self.readUByte())[2:].zfill(8))
                settings = [bool(int(value)) for value in settings]
                node_data['frames_settings'] = settings
                for frame in range(frames_count):
                    frame_data = {}

                    frame_data['frame_id'] = self.readUShort()
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
        Writer.__init__(self)

        self.writeUShort(len(self.get('nodes')))
        for node in self.get('nodes'):
            self.writeString(node['name'])
            self.writeString(node['parent'])

            self.writeUShort(1 if node['has_target'] else 0)
            if node['has_target']:
                self.writeChar(node['target_type'])
                self.writeString(node['target'])
                self.writeUShort(len(node['binds']))
                for bind in node['binds']:
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


class WEND(Chunk, Writer, Reader):
    def __init__(self, header=None):
        super().__init__(header)
        self.chunk_name = 'WEND'

    def parse(self, buffer: bytes):
        Reader.__init__(self, buffer)

    def encode(self):
        Writer.__init__(self)

        self.length = len(self.buffer)


__all__ = [
    'HEAD',
    'MATE',
    'GEOM',
    'CAME',
    'NODE',
    'WEND'
]
