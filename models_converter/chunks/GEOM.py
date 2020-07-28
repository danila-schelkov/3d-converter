from ..utils.reader import Reader
from ..utils.writer import Writer


class Decoder(Reader):
    def __init__(self, initial_bytes: bytes, header: dict):
        super().__init__(initial_bytes)

        # Variables
        self.readed = {}
        vertices = []
        bind_matrix = []
        joints = []
        vertex_weights = []
        weights = []
        vcount = []
        materials = []
        # Variables

        name = self.readString()
        group = self.readString()
        if header['version'] < 2:
            matrix = []
            for x in range(4):
                temp_list = []
                for x1 in range(4):
                    temp_list.append(self.readFloat())
                matrix.append(temp_list)
        vertex_count = self.readUByte()
        for x in range(vertex_count):
            vertex = []
            vertex_type = self.readString()
            vertex_index = self.readUByte()
            vertex_shorts = self.readUShort()
            vertex_scale = self.readFloat()
            vertex_count = self.readUInt32()
            for x1 in range(vertex_count):
                coordinates_massive = []
                for x2 in range(vertex_shorts):
                    coordinate = self.readShort()
                    coordinates_massive.append(coordinate / 32512)
                if vertex_type == 'TEXCOORD':
                    coordinates_massive[1::2] = [1-x for x in coordinates_massive[1::2]]
                vertex.append(coordinates_massive)
            vertices.append({'type': vertex_type, 'index': vertex_index, 'scale': vertex_scale, 'vertex': vertex})
        have_bind_matrix = self.readBool()
        if have_bind_matrix:
            for x in range(16):
                bind_matrix.append(self.readFloat())
        joint_counts = self.readUByte()
        for x in range(joint_counts):
            joint_matrix = []
            joint_name = self.readString()
            for x1 in range(16):
                joint_matrix.append(self.readFloat())
            joints.append({'name': joint_name, 'matrix': joint_matrix})
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
            temp_list = [[joint_a, weight_a], [joint_b, weight_b], [joint_c, weight_c], [joint_d, weight_d]]
            for pair in temp_list:
                if pair[0] != 0:
                    vcount[x] += 1
                    vertex_weights.append(pair[0])
                    if pair[1]/65535 not in weights:
                        weights.append(pair[1]/65535)
                    vertex_weights.append(weights.index(pair[1]/65535))
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
            materials.append({'name': material_name, 'polygons': polygons})

        self.readed['name'] = name
        self.readed['group'] = group
        self.readed['vertices'] = vertices
        self.readed['have_bind_matrix'] = have_bind_matrix
        if have_bind_matrix:
            self.readed['bind_matrix'] = bind_matrix
            self.readed['joints'] = joints
            self.readed['weights'] = {}
            self.readed['weights']['vcount'] = vcount
            self.readed['weights']['weights'] = weights
            self.readed['weights']['vertex_weights'] = vertex_weights
        self.readed['materials'] = materials


class Encoder(Writer):
    def __init__(self, data: dict):
        super().__init__()
        self.name = 'GEOM'
        self.data = data

        self.encode()

        self.length = len(self.buffer)
        
    def encode(self):
        self.writeString(self.data['name'])
        self.writeString(self.data['group'])

        self.encode_vertices(self.data['vertices'])

        self.writeBool(self.data['have_bind_matrix'])
        if self.data['have_bind_matrix']:
            for x in self.data['bind_matrix']:
                self.writeFloat(x)

        self.encode_joints()

        self.encode_weight()

        self.encode_triangles()

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
                    coordinate /= vertex['scale']
                    coordinate *= 32512
                    self.writeShort(round(coordinate))

    def encode_joints(self):
        if self.data['have_bind_matrix']:
            self.writeUByte(len(self.data['joints']))

            for joint in self.data['joints']:
                self.writeString(joint['name'])
                for x in joint['matrix']:
                    self.writeFloat(x)
        else:
            self.writeUByte(0)

    def encode_weight(self):
        if self.data['have_bind_matrix']:
            self.writeUInt32(len(self.data['weights']['vcount']))
            past_index = 0
            for vcount in self.data['weights']['vcount']:
                temp_list = []
                for x in range(vcount):
                    vertex_weights_index = x * 2 + past_index * 2
                    joint_id = self.data['weights']['vertex_weights'][vertex_weights_index]
                    weight_id = self.data['weights']['vertex_weights'][vertex_weights_index + 1]

                    weight = self.data['weights']['weights'][weight_id]

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

    def encode_triangles(self):
        self.writeUByte(len(self.data['materials']))
        for material in self.data['materials']:
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
            if short_length == 2:
                for points in material['polygons']:
                    for point in points:
                        for vertex in point:
                            self.writeUShort(vertex)
            elif short_length == 1:
                for points in material['polygons']:
                    for point in points:
                        for vertex in point:
                            self.writeUByte(vertex)
