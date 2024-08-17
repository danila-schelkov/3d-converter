from __future__ import annotations

from typing import TYPE_CHECKING, cast

from . import Chunk
from ...universal import Geometry

if TYPE_CHECKING:
    from models_converter.formats.scw.chunks.head import HEAD


class GEOM(Chunk):
    chunk_name = "GEOM"

    def __init__(self, geometry: Geometry | None = None):
        self.geometry: Geometry | None = geometry

    def parse(self, buffer: bytes, header: HEAD | None = None) -> None:
        super().parse(buffer)

        assert header is not None

        self.geometry = Geometry(
            name=cast(str, self.read_string()), group=self.read_string()
        )

        if header.version < 2:
            matrix = []
            for x in range(4):
                temp_list = []
                for x1 in range(4):
                    temp_list.append(self.read_float())
                matrix.append(temp_list)

        self._parse_vertices()
        self._parse_skin()
        self._parse_materials()

    def _parse_vertices(self):
        assert self.geometry is not None

        vertex_count = self.read_unsigned_int8()
        for _ in range(vertex_count):
            vertex_type = cast(str, self.read_string())
            vertex_index = self.read_unsigned_int8()
            self.read_unsigned_int8()  # sub_index
            vertex_stride = self.read_unsigned_int8()
            vertex_scale = self.read_float()
            vertex_count = self.read_unsigned_int32()

            if vertex_type == "VERTEX":
                vertex_type = "POSITION"

            coordinates = []
            for _ in range(vertex_count):
                coordinates_massive = [
                    self.read_normalized_int16() for _ in range(vertex_stride)
                ]

                if vertex_type == "TEXCOORD":
                    coordinates_massive[1::2] = [
                        1 - v for v in coordinates_massive[1::2]
                    ]
                coordinates.append(coordinates_massive)

            self.geometry.add_vertex(
                Geometry.Vertex(
                    name=f"{vertex_type.lower()}_0",
                    vertex_type=vertex_type,
                    vertex_index=vertex_index,
                    vertex_scale=vertex_scale,
                    points=coordinates,
                )
            )

    def _parse_skin(self):
        assert self.geometry is not None

        has_controller = self.read_boolean()
        if has_controller:
            self.geometry.set_controller_bind_matrix(
                [self.read_float() for _ in range(16)]
            )

        self._parse_joints()
        self._parse_weights()

    def _parse_joints(self):
        assert self.geometry is not None

        joint_counts = self.read_unsigned_int8()
        for x in range(joint_counts):
            joint_name = self.read_string()
            joint_matrix = [self.read_float() for _ in range(16)]

            self.geometry.add_joint(Geometry.Joint(joint_name, joint_matrix))

    def _parse_weights(self):
        assert self.geometry is not None

        vertex_weights_count = self.read_unsigned_int32()
        for x in range(vertex_weights_count):
            joint_a = self.read_unsigned_int8()
            joint_b = self.read_unsigned_int8()
            joint_c = self.read_unsigned_int8()
            joint_d = self.read_unsigned_int8()
            weight_a = self.read_normalized_unsigned_int16()
            weight_b = self.read_normalized_unsigned_int16()
            weight_c = self.read_normalized_unsigned_int16()
            weight_d = self.read_normalized_unsigned_int16()

            self.geometry.add_weight(Geometry.Weight(joint_a, weight_a))
            self.geometry.add_weight(Geometry.Weight(joint_b, weight_b))
            self.geometry.add_weight(Geometry.Weight(joint_c, weight_c))
            self.geometry.add_weight(Geometry.Weight(joint_d, weight_d))

    def _parse_materials(self):
        assert self.geometry is not None

        materials_count = self.read_unsigned_int8()
        for x in range(materials_count):
            material_name = self.read_string()
            self.read_string()
            triangles_count = self.read_unsigned_int16()
            inputs_count = self.read_unsigned_int8()
            vertex_index_length = self.read_unsigned_int8()

            triangles = []
            for x1 in range(triangles_count):
                triangles.append(
                    [
                        [
                            self.read_unsigned_integer(vertex_index_length)  # Vertex
                            for _ in range(inputs_count)
                        ]
                        for _ in range(3)  # 3 points
                    ]
                )

            self.geometry.add_primitive(
                Geometry.Primitive(
                    cast(str, material_name), triangles, self.geometry.get_vertices()
                )
            )

    def encode(self, header) -> None:
        super().encode()

        assert self.geometry is not None

        self.write_string(self.geometry.get_name())
        self.write_string(self.geometry.get_group())

        # Join vertices with same type
        added_vertices_types: list[str] = []
        joined_vertices: list[Geometry.Vertex] = []

        for vertex in self.geometry.get_vertices():
            if vertex.get_type() in added_vertices_types:
                joined_vertices[
                    added_vertices_types.index(vertex.get_type())
                ].get_points().extend(vertex.get_points())
                continue

            added_vertices_types.append(vertex.get_type())
            joined_vertices.append(vertex)

        self._encode_vertices(joined_vertices)

        self._encode_skin()

        self._encode_materials()

        self.length = len(self.buffer)

    def _encode_vertices(self, vertices: list[Geometry.Vertex]):
        self.write_unsigned_int8(len(vertices))
        for vertex in vertices:
            self.write_string(vertex.get_type())
            self.write_unsigned_int8(vertex.get_index())
            self.write_unsigned_int8(0)  # sub_index
            self.write_unsigned_int8(vertex.get_point_size())
            self.write_float(vertex.get_scale())
            self.write_unsigned_int32(len(vertex.get_points()))
            for point in vertex.get_points():
                if vertex.get_type() == "TEXCOORD":
                    point[1::2] = [1 - v for v in point[1::2]]
                for coordinate in point:
                    self.write_int16(round(coordinate))

    def _encode_skin(self):
        assert self.geometry is not None

        self.write_boolean(self.geometry.has_controller())
        if self.geometry.has_controller():
            for x in self.geometry.get_bind_matrix():
                self.write_float(x)

        self._encode_joints()
        self._encode_weight()

    def _encode_joints(self):
        assert self.geometry is not None

        if not self.geometry.has_controller():
            self.write_unsigned_int8(0)
            return

        self.write_unsigned_int8(len(self.geometry.get_joints()))

        for joint in self.geometry.get_joints():
            self.write_string(joint.get_name())
            for x in joint.get_matrix():
                self.write_float(x)

    def _encode_weight(self):
        assert self.geometry is not None

        if not self.geometry.has_controller():
            self.write_unsigned_int32(0)
            return

        weights_quads = len(self.geometry.get_weights()) // 4
        self.write_unsigned_int32(weights_quads)
        for quad_index in range(weights_quads):
            quad = self.geometry.get_weights()[quad_index * 4 : (quad_index + 1) * 4]
            for weight in quad:
                self.write_unsigned_int8(weight.get_joint_index())
            for weight in quad:
                self.write_normalized_unsigned_int16(weight.get_strength())

    def _encode_materials(self):
        assert self.geometry is not None

        self.write_unsigned_int8(len(self.geometry.get_primitives()))
        for primitive in self.geometry.get_primitives():
            self.write_string(primitive.get_material_name())
            self.write_string("")
            self.write_unsigned_int16(len(primitive.get_triangles()))

            # Calculate settings
            inputs_count = len(primitive.get_input_vertices())

            maximal_value = 0
            for triangle in primitive.get_triangles():
                for point in triangle:
                    for vertex in point:
                        if vertex > maximal_value:
                            maximal_value = vertex

            item_length = 1 if maximal_value <= 255 else 2

            # Write Settings
            self.write_unsigned_int8(inputs_count)
            self.write_unsigned_int8(item_length)

            # Write Polygons
            for triangle in primitive.get_triangles():
                for point in triangle:
                    for vertex in point:
                        self.write_unsigned_integer(vertex, item_length)
