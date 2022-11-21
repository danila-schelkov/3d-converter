from . import Chunk
from ...universal import Geometry


class GEOM(Chunk):
    def __init__(self, header):
        super().__init__(header)
        self.chunk_name = 'GEOM'

        self.geometry: Geometry or None = None

    def parse(self, buffer: bytes):
        super().parse(buffer)

        self.geometry = Geometry(
            name=self.readString(),
            group=self.readString()
        )

        if self.header.version < 2:
            matrix = []
            for x in range(4):
                temp_list = []
                for x1 in range(4):
                    temp_list.append(self.readFloat())
                matrix.append(temp_list)

        self._parse_vertices()
        self._parse_skin()
        self._parse_materials()

    def _parse_vertices(self):
        vertex_count = self.readUByte()
        for _ in range(vertex_count):
            vertex_type = self.readString()
            vertex_index = self.readUByte()
            self.readUByte()  # sub_index
            vertex_stride = self.readUByte()
            vertex_scale = self.readFloat() / 32512
            vertex_count = self.readUInt32()

            if vertex_type == 'VERTEX':
                vertex_type = 'POSITION'

            coordinates = []
            for _ in range(vertex_count):
                coordinates_massive = [self.readShort() for _ in range(vertex_stride)]

                if vertex_type == 'TEXCOORD':
                    coordinates_massive[1::2] = [1 - v for v in coordinates_massive[1::2]]
                coordinates.append(coordinates_massive)

            self.geometry.add_vertex(Geometry.Vertex(
                name=f'{vertex_type.lower()}_0',
                vertex_type=vertex_type,
                vertex_index=vertex_index,
                vertex_scale=vertex_scale,
                points=coordinates)
            )

    def _parse_skin(self):
        has_controller = self.readBool()
        if has_controller:
            self.geometry.set_controller_bind_matrix([self.readFloat() for _ in range(16)])

        self._parse_joints()
        self._parse_weights()

    def _parse_joints(self):
        joint_counts = self.readUByte()
        for x in range(joint_counts):
            joint_name = self.readString()
            joint_matrix = [self.readFloat() for _ in range(16)]

            self.geometry.add_joint(Geometry.Joint(joint_name, joint_matrix))

    def _parse_weights(self):
        vertex_weights_count = self.readUInt32()
        for x in range(vertex_weights_count):
            joint_a = self.readUByte()
            joint_b = self.readUByte()
            joint_c = self.readUByte()
            joint_d = self.readUByte()
            weight_a = self.readNUShort()
            weight_b = self.readNUShort()
            weight_c = self.readNUShort()
            weight_d = self.readNUShort()

            self.geometry.add_weight(Geometry.Weight(joint_a, weight_a))
            self.geometry.add_weight(Geometry.Weight(joint_b, weight_b))
            self.geometry.add_weight(Geometry.Weight(joint_c, weight_c))
            self.geometry.add_weight(Geometry.Weight(joint_d, weight_d))

    def _parse_materials(self):
        materials_count = self.readUByte()
        for x in range(materials_count):
            material_name = self.readString()
            self.readString()
            triangles_count = self.readUShort()
            inputs_count = self.readUByte()
            vertex_index_length = self.readUByte()

            triangles = []
            for x1 in range(triangles_count):
                triangles.append([
                    [
                        self.readUInteger(vertex_index_length)  # Vertex
                        for _ in range(inputs_count)
                    ] for _ in range(3)  # 3 points
                ])

            self.geometry.add_material(Geometry.Material(material_name, triangles, self.geometry.get_vertices()))

    def encode(self):
        super().encode()

        self.writeString(self.geometry.get_name())
        self.writeString(self.geometry.get_group())

        self._encode_vertices(self.geometry.get_vertices())

        self._encode_skin()

        self._encode_materials()

        self.length = len(self.buffer)

    def _encode_vertices(self, vertices):
        self.writeUByte(len(vertices))
        for vertex in vertices:
            self.writeString(vertex.get_type())
            self.writeUByte(vertex.get_index())
            self.writeUByte(0)  # sub_index
            self.writeUByte(vertex.get_point_size())
            self.writeFloat(vertex.get_scale() * 32512)
            self.writeUInt32(len(vertex.get_points()))
            for point in vertex.get_points():
                if vertex.get_type() == 'TEXCOORD':
                    point[1::2] = [1 - v for v in point[1::2]]
                for coordinate in point:
                    self.writeShort(round(coordinate))

    def _encode_skin(self):
        self.writeBool(self.geometry.has_controller())
        if self.geometry.has_controller():
            for x in self.geometry.get_bind_matrix():
                self.writeFloat(x)

        self._encode_joints()
        self._encode_weight()

    def _encode_joints(self):
        if not self.geometry.has_controller():
            self.writeUByte(0)
            return

        self.writeUByte(len(self.geometry.get_joints()))

        for joint in self.geometry.get_joints():
            self.writeString(joint.get_name())
            for x in joint.get_matrix():
                self.writeFloat(x)

    def _encode_weight(self):
        if not self.geometry.has_controller():
            self.writeUInt32(0)
            return

        weights_quads = len(self.geometry.get_weights()) // 4
        self.writeUInt32(weights_quads)
        for quad_index in range(weights_quads):
            quad = self.geometry.get_weights()[quad_index * 4:(quad_index + 1) * 4]
            for weight in quad:
                self.writeUByte(weight.get_joint_index())
            for weight in quad:
                self.writeNUShort(weight.get_strength())

    def _encode_materials(self):
        self.writeUByte(len(self.geometry.get_materials()))
        for material in self.geometry.get_materials():
            self.writeString(material.get_name())
            self.writeString('')
            self.writeUShort(len(material.get_triangles()))

            # Calculate settings
            inputs_count = len(material.get_triangles()[0][0])

            maximal_value = 0
            for triangle in material.get_triangles():
                for point in triangle:
                    for vertex in point:
                        if vertex > maximal_value:
                            maximal_value = vertex

            item_length = 1 if maximal_value <= 255 else 2

            # Write Settings
            self.writeUByte(inputs_count)
            self.writeUByte(item_length)

            # Write Polygons
            for triangle in material.get_triangles():
                for point in triangle:
                    for vertex in point:
                        self.writeUInteger(vertex, item_length)
