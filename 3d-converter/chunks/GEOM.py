<<<<<<< Updated upstream:3d-converter/chunks/GEOM.py
from utils.reader import Reader
from utils.writer import Writer
=======
from ..utils.reader import Reader
from ..utils.writer import Writer
from .chunk import Chunk
>>>>>>> Stashed changes:models_converter/chunks/GEOM.py


class Decoder(Chunk, Reader):
    def __init__(self, header: dict):
        super().__init__(header)

<<<<<<< Updated upstream:3d-converter/chunks/GEOM.py
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
        if header['version'] == 1:
            matrix = []
=======
        self.inputs = []

    def parse(self, initial_bytes: bytes):
        super().__init__(initial_bytes)

        self.parsed['name'] = self.readString()
        self.parsed['group'] = self.readString()
        if self.header['version'] < 2:
            # matrix = []
>>>>>>> Stashed changes:models_converter/chunks/GEOM.py
            for x in range(4):
                # temp_list = []
                for x1 in range(4):
                    self.readFloat()
                    # temp_list.append()
                # matrix.append(temp_list)

        self.parse_vertices()
        self.parse_skin()
        self.parse_materials()

    def parse_vertices(self):
        self.parsed['vertices'] = []

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
                    coordinates_massive.append(self.readNShort())

                if vertex_type == 'TEXCOORD':
                    coordinates_massive[1::2] = [1-x for x in coordinates_massive[1::2]]
                vertex.append(coordinates_massive)
<<<<<<< Updated upstream:3d-converter/chunks/GEOM.py
            vertices.append({'type': vertex_type, 'index': vertex_index, 'scale': vertex_scale, 'vertex': vertex})
=======

            self.inputs.append({
                'type': vertex_type,
                'offset': x,
                'name': f'{vertex_type.lower()}_0'
            })

            self.parsed['vertices'].append({
                'name': f'{vertex_type}_0',
                'type': vertex_type,
                'index': vertex_index,
                'scale': vertex_scale,
                'vertex': vertex
            })

    def parse_skin(self):
        self.parsed['bind_matrix'] = []
        self.parsed['joints'] = []
        self.parsed['weights'] = {
            'vertex_weights': [],
            'weights': [],
            'vcount': []
        }

>>>>>>> Stashed changes:models_converter/chunks/GEOM.py
        have_bind_matrix = self.readBool()
        if have_bind_matrix:
            for x in range(16):
                self.parsed['bind_matrix'].append(self.readFloat())
        joint_counts = self.readUByte()
        for x in range(joint_counts):
            joint_matrix = []
            joint_name = self.readString()
            for x1 in range(16):
                joint_matrix.append(self.readFloat())

            self.parsed['joints'].append({
                'name': joint_name,
                'matrix': joint_matrix
            })
        vertex_weights_count = self.readUInt32()
        for x in range(vertex_weights_count):
            self.parsed['weights']['vcount'].append(0)
            joint_a = self.readUByte()
            joint_b = self.readUByte()
            joint_c = self.readUByte()
            joint_d = self.readUByte()
<<<<<<< Updated upstream:3d-converter/chunks/GEOM.py
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
=======
            weight_a = self.readNUShort()
            weight_b = self.readNUShort()
            weight_c = self.readNUShort()
            weight_d = self.readNUShort()
            temp_list = [
                [joint_a, weight_a],
                [joint_b, weight_b],
                [joint_c, weight_c],
                [joint_d, weight_d]
            ]
            for pair in temp_list:
                if pair[1] != 0:
                    self.parsed['weights']['vcount'][x] += 1
                    self.parsed['weights']['vertex_weights'].append(pair[0])
                    if pair[1] not in self.parsed['weights']['weights']:
                        self.parsed['weights']['weights'].append(pair[1])
                    self.parsed['weights']['vertex_weights'].append(
                        self.parsed['weights']['weights'].index(pair[1])
                    )

    def parse_materials(self):
        materials = []

>>>>>>> Stashed changes:models_converter/chunks/GEOM.py
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
<<<<<<< Updated upstream:3d-converter/chunks/GEOM.py
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
=======
            materials.append({
                'name': material_name,
                'inputs': self.inputs,
                'polygons': polygons
            })

        self.parsed['materials'] = materials
>>>>>>> Stashed changes:models_converter/chunks/GEOM.py


class Encoder(Chunk, Writer):
    def __init__(self):
        super().__init__()
        self.name = 'GEOM'
        
    def encode(self, data: dict):
        self.data = data

        self.writeString(self.data['name'])
        self.writeString(self.data['group'])

        self.encode_vertices(self.data['vertices'])

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
<<<<<<< Updated upstream:3d-converter/chunks/GEOM.py
                    coordinate /= vertex['scale']
                    coordinate *= 32512
                    self.writeShort(round(coordinate))
=======
                    # coordinate /= vertex['scale']
                    self.writeNShort(coordinate)
>>>>>>> Stashed changes:models_converter/chunks/GEOM.py

    def encode_skin(self):
        self.writeBool(self.data['have_bind_matrix'])
        if self.data['have_bind_matrix']:
            for x in self.data['bind_matrix']:
                self.writeFloat(x)

        self.writeUByte(len(self.data['joints']))

        for joint in self.data['joints']:
            self.writeString(joint['name'])
            for x in joint['matrix']:
                self.writeFloat(x)

        self.encode_weight()

    def encode_weight(self):
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

                temp_list.append([joint_id, weight])
            past_index += vcount
            while len(temp_list) < 4:
                temp_list.append([0, 0])
            for x in temp_list:
                self.writeUByte(x[0])
            for x in temp_list:
                self.writeNUShort(x[1])

    def encode_materials(self):
        self.writeUByte(len(self.data['materials']))
        for material in self.data['materials']:
            self.writeString(material['name'])
            self.writeString('')
            self.writeUShort(len(material['polygons']))

            # Calculate settings
            inputs_count = len(material['polygons'][0][0])

            maximal_value = max(max(max(material['polygons'])))
            short_length = 1 if maximal_value <= 255 else 2

            # Write Settings
            self.writeUByte(inputs_count)
            self.writeUByte(short_length)

            # Write Polygons
            if short_length == 2:
                for x in material['polygons']:
                    for x1 in x:
                        for x2 in x1:
                            self.writeShort(x2)
            elif short_length == 1:
                for x in material['polygons']:
                    for x1 in x:
                        for x2 in x1:
                            self.writeByte(x2)
