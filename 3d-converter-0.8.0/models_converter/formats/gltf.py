import json

from models_converter.formats.dae import Writer
from models_converter.utils.reader import Reader


def to_camelcase(property_name: str):
    words = property_name.split('_')
    for word_index in range(len(words)):
        word = words[word_index]
        if word_index > 0:
            word = list(word)
            word[0] = word[0].upper()

            word = ''.join(word)

        words[word_index] = word
    camelcase_name = ''.join(words)
    return camelcase_name


def to_lowercase(property_name: str):
    letters = list(property_name)

    for letter_index in range(len(letters)):
        letter = letters[letter_index]

        if letter.isupper():
            letter = f'_{letter.lower()}'

        letters[letter_index] = letter

    lowercase_name = ''.join(letters)
    return lowercase_name


def get_data_from_dict(dictionary, key, default=None):
    if key in dictionary:
        return dictionary[key]
    return default


from_dict = get_data_from_dict


class GlTFProperty:
    def __init__(self):
        self.extensions = None
        self.extras = None

    def from_dict(self, dictionary: dict):
        if dictionary:
            for key, value in dictionary.items():
                attribute_name = to_lowercase(key)
                value_type = type(value)

                attribute_value = getattr(self, attribute_name)
                attribute_value_type = type(attribute_value)

                if attribute_value is None or value_type in [int, str]:
                    attribute_value = value
                elif issubclass(attribute_value_type, GlTFProperty):
                    if value_type is list:
                        value_type = attribute_value_type
                        values = []

                        for item in value:
                            new_value = value_type()
                            new_value.from_dict(item)

                            values.append(new_value)

                        attribute_value = values
                    else:
                        attribute_value = attribute_value_type()
                        attribute_value.from_dict(value)

                setattr(self, attribute_name, attribute_value)

    def to_dict(self) -> dict:
        dictionary = {}
        for key, value in self.__dict__.items():
            if value is not None:
                attribute_name = to_camelcase(key)
                value_type = type(value)

                attribute_value = None

                if value_type is list:
                    attribute_value = []
                    for item in value:
                        item_type = type(item)

                        if issubclass(item_type, GlTFProperty):
                            item = item.to_dict()
                        attribute_value.append(item)
                elif issubclass(value_type, GlTFProperty):
                    attribute_value = value.to_dict()
                elif attribute_value is None:
                    attribute_value = value

                dictionary[attribute_name] = attribute_value
        return dictionary

    def __getitem__(self, item):
        item = to_lowercase(item)
        if hasattr(self, item):
            return getattr(self, item)
        else:
            raise IndexError('The object has no attribute named ' + item)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} ({self.to_dict()})>'


class Accessor(GlTFProperty):
    class Sparse(GlTFProperty):
        class Indices(GlTFProperty):
            def __init__(self):
                super().__init__()
                self.buffer_view = None
                self.component_type = None

                self.byte_offset = 0

        class Values(GlTFProperty):
            def __init__(self):
                super().__init__()
                self.buffer_view = None

                self.byte_offset = 0

        def __init__(self):
            super().__init__()
            self.count = None
            self.indices = self.Indices()
            self.values = self.Values()

    def __init__(self):
        super().__init__()
        self.component_type = None
        self.count = None
        self.type = None

        self.buffer_view = None
        self.byte_offset = 0
        self.normalized = False
        self.max = None
        self.min = None
        self.sparse = self.Sparse()
        self.name = None


class Animation(GlTFProperty):
    class AnimationSampler(GlTFProperty):
        def __init__(self):
            super().__init__()
            self.input = None
            self.output = None

            self.interpolation = None  # Default: 'LINEAR'

    class Channel(GlTFProperty):
        class Target(GlTFProperty):
            def __init__(self):
                super().__init__()
                self.path = None

                self.node = None

        def __init__(self):
            super().__init__()
            self.sampler = None
            self.target = self.Target()

    def __init__(self):
        super().__init__()
        self.channels = self.Channel()
        self.samplers = self.AnimationSampler()

        self.name = None


class Asset(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.version = None

        self.copyright = None
        self.generator = None
        self.min_version = None


class Buffer(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.byte_length = None

        self.uri = None
        self.name = None


class BufferView(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.buffer = None
        self.byte_length = None

        self.byte_offset = 0
        self.byte_stride = None
        self.target = None
        self.name = None


class Camera(GlTFProperty):
    class Orthographic(GlTFProperty):
        def __init__(self):
            super().__init__()
            self.xmag = None
            self.ymag = None
            self.zfar = None
            self.znear = None

    class Perspective(GlTFProperty):
        def __init__(self):
            super().__init__()
            self.yfov = None
            self.znear = None

            self.aspect_ratio = None
            self.zfar = None

    def __init__(self):
        super().__init__()
        self.type = None

        self.orthographic = None
        self.perspective = None
        self.name = None


class Image(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.uri = None
        self.mime_type = None
        self.buffer_view = None
        self.name = None


class Material(GlTFProperty):
    class NormalTextureInfo(GlTFProperty):
        def __init__(self):
            super().__init__()
            self.index = None

            self.tex_coord = None  # Default: 0
            self.scale = None  # Default: 1

    class OcclusionTextureInfo(GlTFProperty):
        def __init__(self):
            super().__init__()
            self.index = None

            self.tex_coord = None  # Default: 0
            self.strength = None  # Default: 1

    class PbrMetallicRoughness(GlTFProperty):
        def __init__(self):
            super().__init__()
            self.base_color_factor = None  # Default: [1, 1, 1, 1]
            self.base_color_texture = None
            self.metallic_factor = None  # Default: 1
            self.roughness_factor = None  # Default: 1
            self.metallic_roughness_texture = None

    def __init__(self):
        super().__init__()
        self.name = None
        self.pbr_metallic_roughness = None
        self.normal_texture = None
        self.occlusion_texture = None
        self.emissive_texture = None
        self.emissive_factor = None  # Default: [0, 0, 0]
        self.alpha_mode = None  # Default: 'OPAQUE'
        self.alpha_cutoff = None  # Default: 0.5
        self.double_sided = None  # Default: False


class Mesh(GlTFProperty):
    class Primitive(GlTFProperty):
        def __init__(self):
            super().__init__()
            self.attributes = None

            self.indices = None
            self.material = None
            self.mode = None  # Default: 4
            self.targets = None

    def __init__(self):
        super().__init__()
        self.primitives = self.Primitive()

        self.weights = None
        self.name = None


class Node(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.camera = None
        self.children = None
        self.skin = None
        self.matrix = None  # Default: [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        self.mesh = None
        self.rotation = None  # Default: [0, 0, 0, 1]
        self.scale = None  # Default: [1, 1, 1]
        self.translation = None  # Default: [0, 0, 0]
        self.weights = None
        self.name = None


class Sampler(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.mag_filter = None
        self.min_filter = None
        self.wrap_s = None  # Default: 10497
        self.wrap_t = None  # Default: 10497
        self.name = None


class Scene(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.nodes = None
        self.name = None


class Skin(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.joints = None

        self.inverse_bind_matrices = None
        self.skeleton = None
        self.name = None


class Texture(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.sampler = None
        self.source = None
        self.name = None


class TextureInfo(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.index = None

        self.tex_coord = None  # Default: 0


class GlTF(GlTFProperty):
    def __init__(self):
        super().__init__()
        self.asset = Asset()

        self.extensions_used = None
        self.extensions_required = None

        self.accessors = Accessor()
        self.animations = Animation()
        self.buffers = Buffer()
        self.buffer_views = BufferView()
        self.cameras = Camera()
        self.images = Image()
        self.materials = Material()
        self.meshes = Mesh()
        self.nodes = Node()
        self.samplers = Sampler()
        self.scene = None
        self.scenes = Scene()
        self.skins = Skin()
        self.textures = Texture()


class GlTFChunk:
    def __init__(self):
        self.chunk_length = 0
        self.chunk_name = b''
        self.data = b''


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
            super().__init__(self.buffer_views[accessor.buffer_view], '<')
            temp_accessor = []

            self.read(accessor.byte_offset)

            types = {
                5120: self.readByte,
                5121: self.readUByte,
                5122: self.readShort,
                5123: self.readUShort,
                5125: self.readUInt32,
                5126: self.readFloat
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

            for x in range(accessor.count):
                temp_list = []
                for i in range(items_count[accessor.type]):
                    temp_list.append(types[accessor.component_type]())
                temp_accessor.append(temp_list)

            if accessor.normalized:
                for item_index, data in enumerate(temp_accessor):
                    new_data = []
                    for item in data:
                        if accessor['component_type'] == 5120:
                            new_data.append(max(item / 127, -1.0))
                        elif accessor['component_type'] == 5121:
                            new_data.append(item / 255)
                        elif accessor['component_type'] == 5122:
                            new_data.append(max(item / 32767, -1.0))
                        elif accessor['component_type'] == 5123:
                            new_data.append(item / 65535)
                        else:
                            new_data.append(item)
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
        # node_name = node_name.split('|')
        # if len(node_name) > 1:
        #     node_name = node_name[1]
        #     parent = node_name[0]
        # else:
        #     node_name = node_name[0]

        # node_name = node_name.split(':')
        # if len(node_name) > 1:
        #     if node_name[1] == 'PIV':
        #         print(node.name, node.translation)
        #     # else:
        #     print(node)
        #     node_name = node_name[0]
        # else:
        #     node_name = node_name[0]

        node_data = {
            'name': node_name,
            'parent': parent,
            'has_target': False,
            'frames': []
        }

        if node.mesh:
            node_data['has_target'] = True
            node_data['target_type'] = 'GEOM'

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
                geometry_data['have_bind_matrix'] = True
                geometry_data['bind_matrix'] = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
                geometry_data['joints'] = []
                node_data['target_type'] = 'CONT'

                skin_id = node.skin
                skin = self.gltf.skins[skin_id]
                bind_matrices = self.accessors[skin.inverse_bind_matrices]

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

            node_data['target'] = geometry_data['name']
            node_data['binds'] = []

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
                    node_data['binds'].append({
                        'symbol': material_name,
                        'target': material_name
                    })

                    for attribute_id in attributes:
                        attribute = attributes[attribute_id]
                        if attribute_id == 'POSITION':
                            position = self.accessors[attribute]

                            geometry_data['vertices'].append({
                                'type': 'POSITION',
                                'name': f'position_{primitive_index}',
                                'index': len(geometry_data['vertices']),
                                'scale': 1,
                                'vertex': position
                            })

                            inputs.append({
                                'type': 'POSITION',
                                'offset': '1',
                                'name': f'position_{primitive_index}',
                            })
                        elif attribute_id == 'NORMAL':
                            normal = self.accessors[attribute]

                            geometry_data['vertices'].append({
                                'type': 'NORMAL',
                                'name': f'normal_{primitive_index}',
                                'index': len(geometry_data['vertices']),
                                'scale': 1,
                                'vertex': normal
                            })

                            inputs.append({
                                'type': 'NORMAL',
                                'offset': '0',
                                'name': f'normal_{primitive_index}',
                            })
                        elif attribute_id.startswith('TEXCOORD'):
                            texcoord = self.accessors[attribute]

                            texcoord = [[item[0], 1 - item[1]] for item in texcoord]

                            geometry_data['vertices'].append({
                                'type': 'TEXCOORD',
                                'name': f'texcoord_{primitive_index}',
                                'index': len(geometry_data['vertices']),
                                'scale': 1,
                                'vertex': texcoord
                            })

                            inputs.append({
                                'type': 'TEXCOORD',
                                'offset': '2',
                                'name': f'texcoord_{primitive_index}',
                            })
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

                    polygons = [
                        [
                            [
                                value[0] + offsets['NORMAL'],
                                value[0] + offsets['POSITION'],
                                value[0] + offsets['TEXCOORD']
                            ] for value in polygons[x:x + 3]
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


if __name__ == '__main__':
    with open('../crow_geo.glb', 'rb') as fh:
        file_data = fh.read()
        fh.close()
    parser = Parser(file_data)
    parser.parse()

    writer = Writer()
    with open('../crow_geo.dae', 'w') as fh:
        fh.write(writer.writen)
        fh.close()
