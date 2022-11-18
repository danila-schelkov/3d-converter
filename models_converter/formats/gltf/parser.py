import json

from models_converter.formats import universal
from models_converter.formats.gltf.chunk import GlTFChunk
from models_converter.formats.gltf.gltf import GlTF
from models_converter.formats.gltf.node import Node
from models_converter.formats.universal import Scene, Geometry
from models_converter.interfaces import ParserInterface
from models_converter.utilities.reader import Reader


class Parser(ParserInterface):
    def __init__(self, data: bytes):
        self.file_data = data

        self.scene = Scene()

        self.version = None
        self.length = None

        self.json_chunk = None
        self.bin_chunk = None

        self.buffer_views = []
        self.accessors = []
        self.buffers = []

        self.gltf = GlTF()

    def parse_bin(self):
        reader = Reader(self.bin_chunk.data, 'little')

        for buffer in self.gltf.buffers:
            parsed_buffer = reader.read(buffer.byte_length)
            self.buffers.append(parsed_buffer)

        for buffer_view in self.gltf.buffer_views:
            reader.__init__(self.buffers[buffer_view.buffer], 'little')

            reader.read(buffer_view.byte_offset)

            length = buffer_view.byte_length
            data = reader.read(length)

            self.buffer_views.append(data)

        for accessor in self.gltf.accessors:
            reader.__init__(self.buffer_views[accessor.buffer_view], 'little')

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

            stride = self.gltf.buffer_views[accessor.buffer_view].byte_stride or default_stride

            elements_per_stride = stride // bytes_per_element
            elements_count = accessor.count * elements_per_stride

            temp_list = []
            for i in range(elements_count):
                temp_list.append(read_type())

            self.accessors.append([
                temp_list[i:i + components_count]
                for i in range(0, elements_count, elements_per_stride)
            ])

    def parse(self):
        reader = Reader(self.file_data, 'little')

        magic = reader.read(4)
        if magic != b'glTF':
            raise TypeError('Wrong file magic! "676c5446" expected, but given is ' + magic.hex())

        self.version = reader.readUInt32()
        self.length = reader.readUInt32()

        self.json_chunk = GlTFChunk()
        self.bin_chunk = GlTFChunk()

        self.json_chunk.chunk_length = reader.readUInt32()
        self.json_chunk.chunk_name = reader.read(4)
        self.json_chunk.data = reader.read(self.json_chunk.chunk_length)

        self.bin_chunk.chunk_length = reader.readUInt32()
        self.bin_chunk.chunk_name = reader.read(4)
        self.bin_chunk.data = reader.read(self.bin_chunk.chunk_length)

        self.gltf.from_dict(json.loads(self.json_chunk.data))

        self.parse_bin()

        scene_id = self.gltf.scene
        scene = self.gltf.scenes[scene_id]

        for node_id in scene.nodes:
            node = self.gltf.nodes[node_id]
            self.parse_node(node)

        # TODO: animations
        # for animation in self.gltf.animations:
        #     for channel in animation.channels:
        #         sampler: Animation.AnimationSampler = animation.samplers[channel.sampler]
        #         input_accessor = self.accessors[sampler.input]

    def parse_node(self, gltf_node: Node, parent: str = None):
        node_name = gltf_node.name.split('|')[-1]

        node = universal.Node(
            name=node_name,
            parent=parent
        )

        # Transform
        translation = gltf_node.translation
        scale = gltf_node.scale
        rotation = gltf_node.rotation

        instance = None
        if gltf_node.mesh is not None and type(self.gltf.meshes) is list:
            mesh = self.gltf.meshes[gltf_node.mesh]
            mesh_name = mesh.name.split('|')

            group = 'GEO'
            name = mesh_name[0]
            if len(mesh_name) > 1:
                group = mesh_name[0]
                name = mesh_name[1]

            geometry = Geometry(name=name, group=group)

            if gltf_node.skin is not None:
                instance = universal.Node.Instance(name=geometry.get_name(), instance_type='CONT')

                geometry.set_controller_bind_matrix([
                    1, 0, 0, translation.x,
                    0, 1, 0, translation.y,
                    0, 0, 1, translation.z,
                    0, 0, 0, 1
                ])

                skin_id = gltf_node.skin
                skin = self.gltf.skins[skin_id]
                bind_matrices = self.accessors[skin.inverse_bind_matrices]
                bind_matrices = [[*m[0::4], *m[1::4], *m[2::4], *m[3::4]] for m in bind_matrices]

                for joint in skin.joints:
                    joint_index = skin['joints'].index(joint)
                    joint_node = self.gltf.nodes[joint]
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

                    triangles = self.accessors[polygons_id]

                    material_name = f'{name}_material'
                    if primitive.material is not None:
                        material = self.gltf.materials[material_id]
                        if 'SC_shader' in material.extensions:
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
                            position = self.accessors[attribute]
                            points = list(map(
                                lambda point: (
                                    point[0] * scale.x,
                                    point[1] * scale.y,
                                    point[2] * scale.z
                                ),
                                position
                            ))
                        elif attribute_id == 'NORMAL':
                            normal = self.accessors[attribute]
                            points = list(map(
                                lambda point: (
                                    point[0] * gltf_node.scale.x,
                                    point[1] * gltf_node.scale.y,
                                    point[2] * gltf_node.scale.z
                                ),
                                normal
                            ))
                        elif attribute_id.startswith('TEXCOORD'):
                            texcoord = self.accessors[attribute]

                            attribute_id = 'TEXCOORD'
                            # TODO: look how to resize it this
                            points = [[item[0], 1 - item[1]] for item in texcoord]
                        elif attribute_id.startswith('JOINTS'):
                            joint_ids = self.accessors[attribute]
                        elif attribute_id.startswith('WEIGHTS'):
                            weights = self.accessors[attribute]

                            for x in range(len(joint_ids)):
                                geometry.add_weight(Geometry.Weight(joint_ids[x][0], weights[x][0]))
                                geometry.add_weight(Geometry.Weight(joint_ids[x][1], weights[x][1]))
                                geometry.add_weight(Geometry.Weight(joint_ids[x][2], weights[x][2]))
                                geometry.add_weight(Geometry.Weight(joint_ids[x][3], weights[x][3]))

                        if points:
                            geometry.add_vertex(Geometry.Vertex(
                                name=f'{attribute_id.lower()}_{primitive_index}',
                                vertex_type=attribute_id,
                                vertex_index=len(geometry.get_vertices()),
                                vertex_scale=1,
                                points=points
                            ))

                    triangles = [
                        [
                            [
                                point[0] + normal_offset,
                                point[0] + position_offset,
                                point[0] + texcoord_offset
                            ] for point in triangles[x:x + 3]
                        ] for x in range(0, len(triangles), 3)
                    ]

                    geometry.add_material(Geometry.Material(material_name, triangles))

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

        if gltf_node.children:
            for child_id in gltf_node.children:
                child = self.gltf.nodes[child_id]
                self.parse_node(child, node_name)
