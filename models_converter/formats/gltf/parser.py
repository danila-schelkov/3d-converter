import json

from models_converter.formats import universal
from models_converter.formats.gltf.chunk import GlTFChunk
from models_converter.formats.gltf.gltf import GlTF
from models_converter.formats.gltf.node import Node
from models_converter.formats.universal import Scene, Geometry
from models_converter.utilities.math import Vector3, Quaternion
from models_converter.utilities.reader import Reader


class Parser(Reader):
    def __init__(self, initial_bytes: bytes):
        super().__init__(initial_bytes, 'little')

        self.magic = self.read(4)
        if self.magic != b'glTF':
            raise TypeError('File Magic isn\'t "glTF"')

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
        super().__init__(self.bin_chunk.data, 'little')

        for buffer in self.gltf.buffers:
            parsed_buffer = self.read(buffer.byte_length)
            self.buffers.append(parsed_buffer)

        for buffer_view in self.gltf.buffer_views:
            super().__init__(self.buffers[buffer_view.buffer], 'little')

            self.read(buffer_view.byte_offset)

            length = buffer_view.byte_length
            data = self.read(length)

            self.buffer_views.append(data)

        for accessor in self.gltf.accessors:
            super().__init__(self.buffer_views[accessor.buffer_view], 'little')
            temp_accessor = []

            self.read(accessor.byte_offset)

            types = {
                5120: (self.readByte, 1),
                5121: (self.readUByte, 1),
                5122: (self.readShort, 2),
                5123: (self.readUShort, 2),
                5125: (self.readUInt32, 4),
                5126: (self.readFloat, 4)
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

            component_nb = items_count[accessor.type]
            read_type, bytes_per_elem = types[accessor.component_type]
            default_stride = bytes_per_elem * component_nb

            stride = self.gltf.buffer_views[accessor.buffer_view].byte_stride or default_stride
            if default_stride == stride:
                for x in range(accessor.count):
                    temp_list = []
                    for i in range(component_nb):
                        temp_list.append(read_type())
                    temp_accessor.append(temp_list)
            else:
                elems_per_stride = stride // bytes_per_elem
                num_elems = (accessor.count - 1) * elems_per_stride + component_nb

                temp_list = []
                for i in range(num_elems):
                    temp_list.append(read_type())

                temp_accessor = [temp_list[x:x + component_nb] for x in range(0, num_elems, elems_per_stride)]

            if accessor.normalized:
                for item_index, data in enumerate(temp_accessor):
                    new_data = []
                    for value in data:
                        if accessor.component_type == 5120:
                            value = max(value / 127, -1.0)
                        elif accessor.component_type == 5121:
                            value /= 255
                        elif accessor.component_type == 5122:
                            value = max(value / 32767, -1.0)
                        elif accessor.component_type == 5123:
                            value /= 65535
                        new_data.append(value)
                    temp_accessor[item_index] = new_data

            self.accessors.append(temp_accessor)

    def parse(self):
        # <FileParsing>

        self.version = self.readUInt32()
        self.length = self.readUInt32()

        self.json_chunk = GlTFChunk()
        self.bin_chunk = GlTFChunk()

        self.json_chunk.chunk_length = self.readUInt32()
        self.json_chunk.chunk_name = self.read(4)
        self.json_chunk.data = self.read(self.json_chunk.chunk_length)

        self.bin_chunk.chunk_length = self.readUInt32()
        self.bin_chunk.chunk_name = self.read(4)
        self.bin_chunk.data = self.read(self.bin_chunk.chunk_length)

        # </FileParsing>

        self.gltf.from_dict(json.loads(self.json_chunk.data))

        self.parse_bin()

        # <JsonParsing>

        scene_id = self.gltf.scene
        scene = self.gltf.scenes[scene_id]

        for node_id in scene.nodes:
            node = self.gltf.nodes[node_id]
            self.parse_node(node)

        # </JsonParsing>

    def parse_node(self, gltf_node: Node, parent: str = None):
        node_name = gltf_node.name

        node = universal.Node(
            name=node_name,
            parent=parent
        )

        instance = None
        if gltf_node.mesh:
            mesh = self.gltf.meshes[gltf_node.mesh]  # TODO: merge _geo.glb and _.*.glb files to fix TypeError
            mesh_name = mesh.name.split('|')

            group = 'GEO'
            name = mesh_name[0]
            if len(mesh_name) > 1:
                group = mesh_name[0]
                name = mesh_name[1]

            geometry = Geometry(name=name, group=group)

            if gltf_node.skin:
                instance = universal.Node.Instance(name=geometry.get_name(), instance_type='CONT')

                geometry.set_controller_bind_matrix([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])

                skin_id = gltf_node.skin
                skin = self.gltf.skins[skin_id]
                bind_matrices = self.accessors[skin.inverse_bind_matrices]
                bind_matrices = [[m[0::4], m[1::4], m[2::4], m[3::4]] for m in bind_matrices]
                for matrix_index in range(len(bind_matrices)):
                    m = bind_matrices[matrix_index]

                    matrix = m[0]
                    matrix.extend(m[1])
                    matrix.extend(m[2])
                    matrix.extend(m[3])

                    bind_matrices[matrix_index] = matrix

                for joint in skin.joints:
                    joint_index = skin['joints'].index(joint)
                    joint_node = self.gltf.nodes[joint]
                    joint_name = joint_node['name']
                    matrix = bind_matrices[joint_index]

                    geometry.add_joint(Geometry.Joint(joint_name, matrix))
            else:
                instance = universal.Node.Instance(name=geometry.get_name(), instance_type='GEOM')

            offsets = {
                'POSITION': 0,
                'NORMAL': 0,
                'TEXCOORD': 0
            }

            for primitive in mesh.primitives:
                if primitive.to_dict() != {}:
                    primitive_index = mesh.primitives.index(primitive)
                    attributes = primitive.attributes
                    material_id = primitive.material
                    polygons_id = primitive.indices

                    triangles = self.accessors[polygons_id]
                    material = self.gltf.materials[material_id]

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
                            points = position
                        elif attribute_id == 'NORMAL':
                            normal = self.accessors[attribute]
                            points = normal
                        elif attribute_id.startswith('TEXCOORD'):
                            texcoord = self.accessors[attribute]

                            texcoord = [[item[0], 1 - item[1]] for item in texcoord]
                            attribute_id = 'TEXCOORD'
                            points = texcoord
                        elif attribute_id.startswith('JOINTS'):
                            joint_ids = self.accessors[attribute]
                        elif attribute_id.startswith('WEIGHTS'):
                            weights = self.accessors[attribute]

                            for x in range(len(joint_ids)):
                                geometry.add_weight(Geometry.Weight(joint_ids[x][0], weights[x][0] / 255))
                                geometry.add_weight(Geometry.Weight(joint_ids[x][1], weights[x][1] / 255))
                                geometry.add_weight(Geometry.Weight(joint_ids[x][2], weights[x][2] / 255))
                                geometry.add_weight(Geometry.Weight(joint_ids[x][3], weights[x][3] / 255))

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
                                point[0] + offsets['NORMAL'],
                                point[0] + offsets['POSITION'],
                                point[0] + offsets['TEXCOORD']
                            ] for point in triangles[x:x + 3]
                        ] for x in range(0, len(triangles), 3)
                    ]

                    geometry.add_material(Geometry.Material(material_name, triangles))

                    for attribute_id in attributes:
                        if attribute_id == 'POSITION':
                            offsets['POSITION'] += len(position)
                        elif attribute_id == 'NORMAL':
                            offsets['NORMAL'] += len(normal)
                        elif attribute_id.startswith('TEXCOORD'):
                            offsets['TEXCOORD'] += len(texcoord)

            self.scene.add_geometry(geometry)

        if instance is not None:
            node.add_instance(instance)

        self.scene.add_node(node)

        if gltf_node.translation or gltf_node.rotation or gltf_node.scale:
            node.add_frame(universal.Node.Frame(0, Vector3(), Vector3(1, 1, 1), Quaternion()))

        if gltf_node.translation:
            node.get_frames()[0].set_position(Vector3(
                gltf_node.translation[0],
                gltf_node.translation[1],
                gltf_node.translation[2]
            ))
        if gltf_node.rotation:
            node.get_frames()[0].set_rotation(Quaternion(
                gltf_node.rotation[0],
                gltf_node.rotation[1],
                gltf_node.rotation[2],
                gltf_node.rotation[3]
            ))
        if gltf_node.scale:
            node.get_frames()[0].set_scale(Vector3(
                gltf_node.scale[0],
                gltf_node.scale[1],
                gltf_node.scale[2]
            ))

        if gltf_node.children:
            for child_id in gltf_node.children:
                child = self.gltf.nodes[child_id]
                self.parse_node(child, node_name)
