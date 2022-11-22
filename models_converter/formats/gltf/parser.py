import json

from models_converter.formats.universal.material import Material
from models_converter.utilities.matrix.matrix4x4 import Matrix4x4

from models_converter.formats import universal
from models_converter.formats.gltf.chunk import GlTFChunk
from models_converter.formats.gltf.gltf import GlTF
from models_converter.formats.gltf.node import Node
from models_converter.formats.universal import Scene, Geometry
from models_converter.interfaces import ParserInterface
from models_converter.utilities.reader import Reader


class Parser(ParserInterface):
    def __init__(self, data: bytes):
        self._file_data = data

        self.scene = Scene()

        self._version: int = 0
        self._length: int = 0

        self._json_chunk: GlTFChunk or None = None
        self._bin_chunk: GlTFChunk or None = None

        self._buffer_views = []
        self._accessors = []
        self._buffers = []

        self._gltf = GlTF()

    def _parse_bin(self):
        reader = Reader(self._bin_chunk.data, 'little')

        for buffer in self._gltf.buffers:
            parsed_buffer = reader.read(buffer.byte_length)
            self._buffers.append(parsed_buffer)

        for buffer_view in self._gltf.buffer_views:
            reader.__init__(self._buffers[buffer_view.buffer], 'little')

            reader.read(buffer_view.byte_offset)

            length = buffer_view.byte_length
            data = reader.read(length)

            self._buffer_views.append(data)

        for accessor in self._gltf.accessors:
            reader.__init__(self._buffer_views[accessor.buffer_view], 'little')

            reader.read(accessor.byte_offset)

            types = {
                5120: (reader.readByte, 1),
                5121: (reader.readUByte, 1),
                5122: (reader.readShort, 2),
                5123: (reader.readUShort, 2),
                5125: (reader.readUInt32, 4),
                5126: (reader.readFloat, 4)
            }

            if accessor.normalized:
                types = {
                    5120: (lambda: max(reader.readByte() / 127, -1.0), 1),
                    5121: (lambda: reader.readUByte() / 255, 1),
                    5122: (lambda: max(reader.readShort() / 32767, -1.0), 2),
                    5123: (lambda: reader.readUShort() / 65535, 2),
                    5125: (reader.readUInt32, 4),
                    5126: (reader.readFloat, 4)
                }

            items_count = {
                'SCALAR': 1,
                'VEC2': 2,
                'VEC3': 3,
                'VEC4': 4,
                'MAT2': 4,
                'MAT3': 9,
                'MAT4': 16
            }

            components_count = items_count[accessor.type]
            read_type, bytes_per_element = types[accessor.component_type]
            default_stride = bytes_per_element * components_count

            stride = self._gltf.buffer_views[accessor.buffer_view].byte_stride or default_stride

            elements_per_stride = stride // bytes_per_element
            elements_count = accessor.count * elements_per_stride

            temp_list = []
            for i in range(elements_count):
                temp_list.append(read_type())

            self._accessors.append([
                temp_list[i:i + components_count]
                for i in range(0, elements_count, elements_per_stride)
            ])

    def parse(self):
        reader = Reader(self._file_data, 'little')

        magic = reader.read(4)
        if magic != b'glTF':
            raise TypeError('Wrong file magic! "676c5446" expected, but given is ' + magic.hex())

        self._version = reader.readUInt32()
        self._length = reader.readUInt32()

        self._json_chunk = GlTFChunk()
        self._bin_chunk = GlTFChunk()

        self._json_chunk.chunk_length = reader.readUInt32()
        self._json_chunk.chunk_name = reader.read(4)
        self._json_chunk.data = reader.read(self._json_chunk.chunk_length)

        self._bin_chunk.chunk_length = reader.readUInt32()
        self._bin_chunk.chunk_name = reader.read(4)
        self._bin_chunk.data = reader.read(self._bin_chunk.chunk_length)

        self._gltf.from_dict(json.loads(self._json_chunk.data))

        self._parse_bin()

        if self._gltf.is_using_extension('SC_shader'):
            self._parse_materials()

        scene_id = self._gltf.scene
        scene = self._gltf.scenes[scene_id]

        for node_id in scene.nodes:
            node = self._gltf.nodes[node_id]
            self._parse_node(node)

        # TODO: animations
        # for animation in self.gltf.animations:
        #     for channel in animation.channels:
        #         sampler: Animation.AnimationSampler = animation.samplers[channel.sampler]
        #         input_accessor = self.accessors[sampler.input]

    def _parse_materials(self):
        for material in self._gltf.materials:
            sc_shader = material.extensions['SC_shader']
            material_name = sc_shader['name']

            self.scene.add_material(Material(
                name=material_name,
                shader='shader/uber.vsh',
                effect=Material.Effect()
            ))

    def _parse_node(self, gltf_node: Node, parent: str = None):
        node_name = gltf_node.name.split('|')[-1]

        if node_name.endswith(':SSC'):  # or node_name.endswith(':PIV')
            self._process_node_children(gltf_node.children, parent)
            return

        node = universal.Node(
            name=node_name,
            parent=parent
        )

        # Transform
        translation = gltf_node.translation
        scale = gltf_node.scale
        rotation = gltf_node.rotation

        instance = None
        if gltf_node.mesh is not None and type(self._gltf.meshes) is list:
            mesh = self._gltf.meshes[gltf_node.mesh]
            mesh_name = mesh.name.split('|')

            group = 'GEO'
            name = mesh_name[0]
            if len(mesh_name) > 1:
                group = mesh_name[0]
                name = mesh_name[1]

            geometry = Geometry(name=name, group=group)

            if gltf_node.skin is not None:
                skin_id = gltf_node.skin
                skin = self._gltf.skins[skin_id]

                instance = universal.Node.Instance(name=geometry.get_name(), instance_type='CONT')

                translation_matrix = Matrix4x4.create_translation_matrix(translation)
                rotation_matrix = Matrix4x4.create_rotation_matrix(rotation)
                scale_matrix = Matrix4x4.create_scale_matrix(scale)

                controller_bind_matrix = translation_matrix @ rotation_matrix @ scale_matrix

                geometry.set_controller_bind_matrix(controller_bind_matrix.get_linear_matrix())

                translation_matrix.inverse()
                rotation_matrix.inverse()
                scale_matrix.inverse()

                inverse_controller_bind_matrix = (translation_matrix @ rotation_matrix @ scale_matrix)

                bind_matrices_accessor = self._accessors[skin.inverse_bind_matrices]
                bind_matrices = []
                for bind_matrix in bind_matrices_accessor:
                    bind_matrix_ = Matrix4x4(matrix=[
                        bind_matrix[0::4],
                        bind_matrix[1::4],
                        bind_matrix[2::4],
                        bind_matrix[3::4]
                    ])

                    bind_matrices.append(
                        (bind_matrix_ @ inverse_controller_bind_matrix).get_linear_matrix()
                    )

                for joint in skin.joints:
                    joint_index = skin['joints'].index(joint)
                    joint_node = self._gltf.nodes[joint]
                    joint_name = joint_node['name']
                    matrix = bind_matrices[joint_index]

                    geometry.add_joint(Geometry.Joint(joint_name, matrix))
            else:
                instance = universal.Node.Instance(name=geometry.get_name(), instance_type='GEOM')

            position_offset = 0
            normal_offset = 0
            texcoord_offset = 0

            for primitive in mesh.primitives:
                if primitive.to_dict() != {}:
                    primitive_index = mesh.primitives.index(primitive)
                    attributes = primitive.attributes
                    material_id = primitive.material
                    polygons_id = primitive.indices
                    input_vertices = []

                    triangles = self._accessors[polygons_id]

                    material_name = f'{name}_material'
                    if primitive.material is not None:
                        material = self._gltf.materials[material_id]
                        if self._gltf.is_using_extension('SC_shader'):
                            material_name = material.extensions['SC_shader']['name']
                    instance.add_bind(material_name, material_name)

                    position = []
                    normal = []
                    texcoord = []

                    joint_ids = 0

                    for attribute_id in attributes:
                        attribute = attributes[attribute_id]
                        points = None

                        if attribute_id == 'POSITION':
                            position = self._accessors[attribute]
                            points = position
                        elif attribute_id == 'NORMAL':
                            normal = self._accessors[attribute]
                            points = normal
                        elif attribute_id.startswith('TEXCOORD'):
                            texcoord = self._accessors[attribute]

                            attribute_id = 'TEXCOORD'
                            # TODO: look how to resize it this
                            points = [[item[0] / 4096, 1 - item[1] / 4096] for item in texcoord]
                        elif attribute_id.startswith('JOINTS'):
                            joint_ids = self._accessors[attribute]
                        elif attribute_id.startswith('WEIGHTS'):
                            weights = self._accessors[attribute]

                            for x in range(len(joint_ids)):
                                geometry.add_weight(Geometry.Weight(joint_ids[x][0], weights[x][0]))
                                geometry.add_weight(Geometry.Weight(joint_ids[x][1], weights[x][1]))
                                geometry.add_weight(Geometry.Weight(joint_ids[x][2], weights[x][2]))
                                geometry.add_weight(Geometry.Weight(joint_ids[x][3], weights[x][3]))

                        if points:
                            vertex = Geometry.Vertex(
                                name=f'{attribute_id.lower()}_{primitive_index}',
                                vertex_type=attribute_id,
                                vertex_index=len(input_vertices),
                                vertex_scale=1,
                                points=points
                            )
                            input_vertices.append(vertex)
                            geometry.add_vertex(vertex)

                    triangles = [
                        [
                            [
                                point[0] + normal_offset,
                                point[0] + position_offset,
                                point[0] + texcoord_offset
                            ] for point in triangles[x:x + 3]
                        ] for x in range(0, len(triangles), 3)
                    ]

                    geometry.add_primitive(Geometry.Primitive(material_name, triangles, input_vertices))

                    for attribute_id in attributes:
                        if attribute_id == 'POSITION':
                            position_offset += len(position)
                        elif attribute_id == 'NORMAL':
                            normal_offset += len(normal)
                        elif attribute_id.startswith('TEXCOORD'):
                            texcoord_offset += len(texcoord)

            self.scene.add_geometry(geometry)

        if instance is not None:
            node.add_instance(instance)

        node.add_frame(universal.Node.Frame(
            0,
            translation,
            scale,
            rotation
        ))

        self.scene.add_node(node)

        self._process_node_children(gltf_node.children, node_name)

    def _process_node_children(self, node_children, node_name):
        if not node_children:
            return

        for child_id in node_children:
            child = self._gltf.nodes[child_id]
            self._parse_node(child, node_name)
