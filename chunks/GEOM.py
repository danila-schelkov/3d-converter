from scw.utils.reader import Reader
from scw.utils.writer import Writer


class Decoder(Reader):
    def __init__(self, initial_bytes: bytes, header: dict):
        super().__init__(initial_bytes)

        # Variables
        self.readed = {}
        vertices = []
        bind_matrix = []
        joints = []
        vertex_weight = []
        weights = []
        vcount = []
        materials = []
        # Variables

        name = self.readString()
        group = self.readString()
        if header['version'] == 1:
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
        vertex_weight_count = self.readUInt32()
        for x in range(vertex_weight_count):
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
                if pair[1] != 0:
                    vcount[x] += 1
                    vertex_weight.append(pair[0])
                    if pair[1] not in weights:
                        weights.append(pair[1]/65535)
                    vertex_weight.append(weights.index(pair[1]/65535))
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
                    temp_list.append([self.readUInteger(vertex_id_length) for x3 in range(inputs_count)])
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
            self.readed['weights']['vertex_weight'] = vertex_weight
        self.readed['materials'] = materials


class Encoder(Writer):
    def __init__(self, info: dict):
        super().__init__()
        self.writeString(info['name'])
        self.writeString(info['group'])
        self.writeUByte(len(info['vertices']))
        for vertex in info['vertices']:
            self.writeString(vertex['type'])
            self.writeUByte(vertex['index'])
            self.writeUShort(len(vertex['vertex'][0]))
            self.writeFloat(vertex['scale'])
            self.writeUInt32(len(vertex['vertex']))
            for coordinates_massive in vertex['vertex']:
                if vertex['type'] == 'TEXCOORD':
                    coordinates_massive[1::2] = [1-x for x in coordinates_massive[1::2]]
                for coordinate in coordinates_massive:
                    coordinate /= vertex['scale']
                    coordinate *= 32512
                    self.writeShort(round(coordinate))
        self.writeBool(info['have_bind_matrix'])
        if info['have_bind_matrix']:
            for x in info['bind_matrix']:
                self.writeFloat(x)
        if info['have_bind_matrix']:
            self.writeUByte(len(info['joints']))

            for joint in info['joints']:
                self.writeString(joint['name'])
                for x in joint['matrix']:
                    self.writeFloat(x)
        else:
            self.writeUByte(0)
        if info['have_bind_matrix']:
            self.writeUInt32(len(info['weights']['vcount']))
            past_index = 0
            for vcount in info['weights']['vcount']:
                temp_list = []
                for x in range(vcount):
                    vertex_weight_index = x * 2 + past_index * 2
                    joint_id = info['weights']['vertex_weight'][vertex_weight_index]
                    weight_id = info['weights']['vertex_weight'][vertex_weight_index + 1]
                    weight = int(info['weights']['weights'][weight_id] * 65535)
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
        self.writeUByte(len(info['materials']))
        for material in info['materials']:
            self.writeString(material['name'])
            self.writeString('')
            self.writeUShort(len(material['polygons']))
            self.writeUByte(len(material['polygons'][0][0]))
            self.writeUByte(2)
            for x in material['polygons']:
                for x1 in x:
                    for x2 in x1:
                        self.writeUShort(x2)