import json

from models_converter.formats.gltf.chunk import GlTFChunk
from models_converter.formats.gltf.gltf import GlTF
from models_converter.formats.gltf.node import Node
from models_converter.utils.reader import Reader


class Parser(Reader):
    def __init__(self, initial_bytes: bytes):
        super().__init__(initial_bytes, 'little')

        self.magic = self.read(4)
        if self.magic != b'glTF':
            raise TypeError('File Magic isn\'t "glTF"')

        self.parsed = {
            'header': {
                'frame_rate': 30
            },
            'materials': [],
            'geometries': [],
            'cameras': [],
            'nodes': []
        }

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

    def parse_node(self, node: Node, parent: str = None):
        node_name = node.name

        node_data = {
            'name': node_name,
            'parent': parent,
            'instances': [],
            'frames': []
        }

        instance = None
        if node.mesh:
            instance = {
                'instance_type': 'GEOM',
                'instance_name': None,
                'binds': []
            }
            geometry_data = {
                'name': '',
                'group': '',
                'vertices': [],
                'have_bind_matrix': False,
                'weights': {
                    'vertex_weights': [],
                    'weights': [],
                    'vcount': []
                },
                'materials': []
            }

            if node.skin:
                instance['instance_type'] = 'CONT'

                geometry_data['have_bind_matrix'] = True
                geometry_data['bind_matrix'] = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
                geometry_data['joints'] = []

                skin_id = node.skin
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

                    joint_data = {
                        'name': joint_name,
                        'matrix': matrix
                    }
                    geometry_data['joints'].append(joint_data)

            mesh_id = node.mesh
            mesh = self.gltf.meshes[mesh_id]
            mesh_name = mesh.name
            mesh_name = mesh_name.split('|')

            if len(mesh_name) > 1:
                geometry_data['group'] = mesh_name[0]
                geometry_data['name'] = mesh_name[1]
            else:
                geometry_data['name'] = mesh_name[0]

            instance['instance_name'] = geometry_data['name']

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

                    inputs = []

                    polygons = self.accessors[polygons_id]
                    material = self.gltf.materials[material_id]

                    material_name = material.extensions['SC_shader']['name']
                    instance['binds'].append({
                        'symbol': material_name,
                        'target': material_name
                    })

                    position = []
                    normal = []
                    texcoord = []

                    vertex_weights = 0

                    for attribute_id in attributes:
                        attribute = attributes[attribute_id]
                        vertex = None

                        if attribute_id == 'POSITION':
                            position = self.accessors[attribute]
                            vertex = position
                        elif attribute_id == 'NORMAL':
                            normal = self.accessors[attribute]
                            vertex = normal
                        elif attribute_id.startswith('TEXCOORD'):
                            texcoord = self.accessors[attribute]

                            texcoord = [[item[0], 1 - item[1]] for item in texcoord]
                            attribute_id = 'TEXCOORD'
                            vertex = texcoord
                        elif attribute_id.startswith('JOINTS'):
                            vertex_weights = self.accessors[attribute]
                        elif attribute_id.startswith('WEIGHTS'):
                            weights = self.accessors[attribute]

                            for x in range(len(vertex_weights)):
                                geometry_data['weights']['vcount'].append(0)

                                temp_list = [
                                    [vertex_weights[x][0], weights[x][0]],
                                    [vertex_weights[x][1], weights[x][1]],
                                    [vertex_weights[x][2], weights[x][2]],
                                    [vertex_weights[x][3], weights[x][3]]
                                ]
                                for pair in temp_list:
                                    if pair[1] != 0:
                                        geometry_data['weights']['vcount'][x] += 1
                                        geometry_data['weights']['vertex_weights'].append(pair[0])
                                        if pair[1] not in geometry_data['weights']['weights']:
                                            geometry_data['weights']['weights'].append(pair[1])
                                        geometry_data['weights']['vertex_weights'].append(
                                            geometry_data['weights']['weights'].index(pair[1])
                                        )
                            for weight_index in range(len(geometry_data['weights']['weights'])):
                                geometry_data['weights']['weights'][weight_index] /= 255

                        if vertex:
                            geometry_data['vertices'].append({
                                'type': attribute_id,
                                'name': f'{attribute_id.lower()}_{primitive_index}',
                                'index': len(geometry_data['vertices']),
                                'scale': 1,
                                'vertex': vertex
                            })

                            inputs.append({
                                'type': attribute_id,
                                'offset': len(inputs),
                                'name': f'{attribute_id.lower()}_{primitive_index}',
                            })

                    polygons = [
                        [
                            [
                                point[0] + offsets['NORMAL'],
                                point[0] + offsets['POSITION'],
                                point[0] + offsets['TEXCOORD']
                            ] for point in polygons[x:x + 3]
                        ] for x in range(0, len(polygons), 3)
                    ]

                    geometry_data['materials'].append({
                        'name': material_name,
                        'inputs': inputs,
                        'polygons': polygons
                    })

                    for attribute_id in attributes:
                        if attribute_id == 'POSITION':
                            offsets['POSITION'] += len(position)
                        elif attribute_id == 'NORMAL':
                            offsets['NORMAL'] += len(normal)
                        elif attribute_id.startswith('TEXCOORD'):
                            offsets['TEXCOORD'] += len(texcoord)

            self.parsed['geometries'].append(geometry_data)

        if instance is not None:
            node_data['instances'].append(instance)

        self.parsed['nodes'].append(node_data)

        if node.translation or node.rotation or node.scale:
            node_data['frames'].append({
                'frame_id': 0,
                'rotation': {'x': 0, 'y': 0, 'z': 0, 'w': 0},
                'position': {'x': 0, 'y': 0, 'z': 0},
                'scale': {'x': 1, 'y': 1, 'z': 1}
            })

        if node.translation:
            node_data['frames'][0]['position'] = {
                'x': node.translation[0],
                'y': node.translation[1],
                'z': node.translation[2]
            }
        if node.rotation:
            node_data['frames'][0]['rotation'] = {
                'x': node.rotation[0],
                'y': node.rotation[1],
                'z': node.rotation[2],
                'w': node.rotation[3]
            }
        if node.scale:
            node_data['frames'][0]['scale'] = {
                'x': node.scale[0],
                'y': node.scale[1],
                'z': node.scale[2]
            }

        if node.children:
            for child_id in node.children:
                child = self.gltf.nodes[child_id]
                self.parse_node(child, node_name)
