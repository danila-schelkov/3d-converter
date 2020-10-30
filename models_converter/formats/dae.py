from xml.etree.ElementTree import *

from ..utils.matrix.matrix4x4 import Matrix4x4


def _(*args):
    print('[ScwUtils]', end=' ')
    for arg in args:
        print(arg, end=' ')
    print()


class Collada:
    def __init__(self):
        self.version = '1.4.1'
        self.xml_namespace = 'http://www.collada.org/2005/11/COLLADASchema'
        self.collada = Element('COLLADA', version=self.version, xmlns=self.xml_namespace)

    @staticmethod
    def write_source(parent,
                     source_id: str,
                     array_tag: str,
                     array_data: list,
                     stride: int,
                     params: list):
        source = SubElement(parent, 'source', id=source_id)

        array = SubElement(source, array_tag)
        array.attrib = {'id': f'{source_id}-array',
                        'count': f'{len(array_data) * stride}'}

        technique_common = SubElement(source, 'technique_common')
        accessor = SubElement(technique_common, 'accessor')
        accessor.attrib = {'source': f'#{source_id}-array',
                           'count': f'{len(array_data)}',
                           'stride': f'{stride}'}

        for param_data in params:
            param = SubElement(accessor, 'param')
            param.attrib = param_data

        array.text = ' '.join(array_data)

    @staticmethod
    def write_input(parent,
                    semantic: str,
                    source_id: str,
                    offset: int = None):
        attributes = {
            'semantic': semantic,
            'source': f'#{source_id}'
        }

        if offset is not None:
            attributes['offset'] = f'{offset}'

        _input = SubElement(parent, 'input')
        _input.attrib = attributes


class Writer:
    def __init__(self):
        self.writen = ''

    def write(self, data: dict):
        dae = Collada()
        asset = SubElement(dae.collada, 'asset')

        # <Libraries>
        library_materials = SubElement(dae.collada, 'library_materials')
        library_effects = SubElement(dae.collada, 'library_effects')
        # library_images = SubElement(dae.collada, 'library_images')
        library_geometries = SubElement(dae.collada, 'library_geometries')
        library_controllers = SubElement(dae.collada, 'library_controllers')
        library_animations = SubElement(dae.collada, 'library_animations')
        # library_cameras = SubElement(dae.collada, 'library_cameras')
        library_visual_scenes = SubElement(dae.collada, 'library_visual_scenes')
        # </Libraries>

        # <Copyright>
        contributor = SubElement(asset, 'contributor')
        SubElement(contributor, 'author').text = 'Vorono4ka'
        SubElement(contributor, 'authoring_tool').text = 'models_converter (https://github.com/vorono4ka/3d-converter)'

        if 'version' in data['header']:
            SubElement(contributor, 'comments').text = 'SCW Version: ' + str(data['header']['version'])
        # </Copyright>

        # <Materials>
        for material_data in data['materials']:
            material_name = material_data['name']

            SubElement(library_materials, 'material', id=material_name)
            effect_name = f'{material_name}-effect'

            material = SubElement(library_materials, 'material', id=material_name)
            SubElement(material, 'instance_effect', url=f'#{effect_name}')

            effect = SubElement(library_effects, 'effect', id=effect_name)
            profile = SubElement(effect, 'profile_COMMON')
            technique = SubElement(profile, 'technique', sid='common')

            ambient_data = material_data['effect']['ambient']
            diffuse_data = material_data['effect']['diffuse']
            emission_data = material_data['effect']['emission']
            specular_data = material_data['effect']['specular']

            phong = SubElement(technique, 'phong')

            if type(ambient_data) is list:
                ambient = SubElement(phong, 'ambient')
                ambient_data[3] /= 255
                ambient_data = [str(item) for item in ambient_data]
                SubElement(ambient, 'color').text = ' '.join(ambient_data)
            # else:
            #     SubElement(ambient, 'texture', texture=ambient_data, texcoord='CHANNEL0')

            if type(diffuse_data) is list:
                diffuse = SubElement(phong, 'diffuse')
                diffuse_data[3] /= 255
                diffuse_data = [str(item) for item in diffuse_data]
                SubElement(diffuse, 'color').text = ' '.join(diffuse_data)
            # else:
            #     SubElement(diffuse, 'texture', texture=diffuse_data, texcoord='CHANNEL0')

            if type(emission_data) is list:
                emission = SubElement(phong, 'emission')
                emission_data[3] /= 255
                emission_data = [str(item) for item in emission_data]
                SubElement(emission, 'color').text = ' '.join(emission_data)
            # else:
            #     SubElement(emission, 'texture', texture=emission_data, texcoord='CHANNEL0')

            if type(specular_data) is list:
                specular = SubElement(phong, 'specular')
                specular_data[3] /= 255
                specular_data = [str(item) for item in specular_data]
                SubElement(specular, 'color').text = ' '.join(specular_data)
            # else:
            #     SubElement(specular, 'texture', texture=specular_data, texcoord='CHANNEL0')
        # </Materials>

        # <Geometries>
        for geometry_data in data['geometries']:
            geometry_name = geometry_data['name']

            geometry = SubElement(library_geometries, 'geometry', id=f'{geometry_name}-geom')
            mesh = SubElement(geometry, 'mesh')

            # <Vertices>
            for vertex_data in geometry_data['vertices']:
                params = []

                vertex_type = vertex_data['type']
                vertex_name = vertex_data['name']
                vertex = vertex_data['vertex']
                stride = len(vertex[0])

                if vertex_type == 'VERTEX':
                    vertex_type = 'POSITION'

                source_name = f'{geometry_name}-{vertex_name}'

                if vertex_type in ['POSITION', 'NORMAL']:
                    params.append({'name': 'X', 'type': 'float'})
                    params.append({'name': 'Y', 'type': 'float'})
                    params.append({'name': 'Z', 'type': 'float'})
                elif vertex_type in ['TEXCOORD']:
                    params.append({'name': 'S', 'type': 'float'})
                    params.append({'name': 'T', 'type': 'float'})

                dae.write_source(
                    mesh,
                    source_name,
                    'float_array',
                    [' '.join([str(sub_item * vertex_data['scale']) for sub_item in item]) for item in vertex],
                    stride,
                    params
                )

                if vertex_type == 'POSITION':
                    vertices = SubElement(mesh, 'vertices', id=f'{source_name}-vertices')
                    dae.write_input(vertices, 'POSITION', source_name)
            # </Vertices>

            # <Polygons>
            for material in geometry_data['materials']:
                polygons_data = material['polygons']
                material_name = material['name']

                triangles = SubElement(mesh, 'triangles',
                                       count=f'{len(polygons_data)}',
                                       material=material_name)
                for _input in material['inputs']:
                    input_offset = _input['offset']
                    input_name = _input['name']
                    input_type = _input['type']

                    if input_type == 'POSITION':
                        input_type = 'VERTEX'
                    source_id = f'{geometry_name}-{input_name}'
                    if input_type == 'VERTEX':
                        source_id = f'{source_id}-vertices'

                    dae.write_input(triangles, input_type, source_id, input_offset)
                polygons = SubElement(triangles, 'p')

                formatted_polygons_data = []
                for polygon in polygons_data:
                    for point in polygon:
                        for vertex in point:
                            formatted_polygons_data.append(str(vertex))

                polygons.text = ' '.join(formatted_polygons_data)
            # </Polygons>

            # <Controller>
            if geometry_data['have_bind_matrix']:
                joints_matrices = []
                joints_names = []

                controller = SubElement(library_controllers, 'controller', id=f'{geometry_name}-cont')
                skin = SubElement(controller, 'skin', source=f'#{geometry_name}-geom')

                if 'bind_matrix' in geometry_data:
                    bind_matrix_data = [str(value) for value in geometry_data['bind_matrix']]
                    SubElement(skin, 'bind_shape_matrix').text = ' '.join(bind_matrix_data)

                for joint in geometry_data['joints']:
                    joints_names.append(joint['name'])
                    joint_matrix = [str(value) for value in joint['matrix']]
                    joint_matrix = ' '.join(joint_matrix)
                    joints_matrices.append(joint_matrix)

                joints_names_source_id = f'{geometry_name}-joints'
                joints_matrices_source_id = f'{geometry_name}-joints-bind-matrices'
                weights_source_id = f'{geometry_name}-weights'

                dae.write_source(
                    skin,
                    joints_names_source_id,
                    'Name_array',
                    joints_names,
                    1,
                    [{'name': 'JOINT', 'type': 'name'}]
                )

                dae.write_source(
                    skin,
                    joints_matrices_source_id,
                    'float_array',
                    joints_matrices,
                    16,
                    [{'name': 'TRANSFORM', 'type': 'float4x4'}]
                )

                dae.write_source(
                    skin,
                    weights_source_id,
                    'float_array',
                    [str(value) for value in geometry_data['weights']['weights']],
                    1,
                    [{'name': 'WEIGHT', 'type': 'float'}]
                )

                joints = SubElement(skin, 'joints')
                dae.write_input(joints, 'JOINT', joints_names_source_id)
                dae.write_input(joints, 'INV_BIND_MATRIX', joints_matrices_source_id)

                vertex_weights_data = [str(value) for value in geometry_data['weights']['vertex_weights']]
                vcount = [str(value) for value in geometry_data['weights']['vcount']]

                vertex_weights = SubElement(skin, 'vertex_weights', count=f'{len(vcount)}')
                dae.write_input(vertex_weights, 'JOINT', joints_names_source_id, 0)
                dae.write_input(vertex_weights, 'WEIGHT', weights_source_id, 1)

                SubElement(vertex_weights, 'vcount').text = ' '.join(vcount)
                SubElement(vertex_weights, 'v').text = ' '.join(vertex_weights_data)
            # </Controller>
        # </Geometries>

        # <Scene>

        visual_scene = SubElement(library_visual_scenes, 'visual_scene',
                                  id='3dConverterScene',
                                  name='3d-Converter Scene')

        for node_data in data['nodes']:
            parent_name = node_data['parent']
            parent = visual_scene
            if parent_name != '':
                parent = visual_scene.find(f'.//*[@id="{parent_name}"]')
                if parent is None:
                    parent = visual_scene
            node_name = node_data['name']

            node = SubElement(parent, 'node', id=node_data['name'])

            for instance in node_data['instances']:
                instance_type = instance['instance_type']
                instance_name = instance['instance_name']
                bind_material = None

                if instance_type == 'CONT':
                    instance_controller = SubElement(node, 'instance_controller', url=f'#{instance_name}-cont')
                    bind_material = SubElement(instance_controller, 'bind_material')
                elif instance_type == 'GEOM':
                    instance_controller = SubElement(node, 'instance_geometry', url=f'#{instance_name}-geom')
                    bind_material = SubElement(instance_controller, 'bind_material')

                if instance_type in ['GEOM', 'CONT']:
                    technique_common = SubElement(bind_material, 'technique_common')
                    for bind in instance['binds']:
                        symbol = bind['symbol']
                        target = bind['target']

                        SubElement(technique_common, 'instance_material',
                                   symbol=symbol,
                                   target=f'#{target}')
            else:
                if parent_name != '' and len(node_data['instances']) == 0:
                    node.attrib['type'] = 'JOINT'

            # <AnimationVariables>
            frame_rate = data['header']['frame_rate']
            time_input = []
            matrix_output = []
            # </AnimationVariables>

            frames = node_data['frames']
            for frame in frames:
                frame_id = frame['frame_id']
                matrix = Matrix4x4(size=(4, 4))

                time_input.append(str(frame_id/frame_rate))

                position_xyz = (frame['position']['x'], frame['position']['y'], frame['position']['z'])
                rotation_xyz = (frame['rotation']['x'], frame['rotation']['y'], frame['rotation']['z'])
                scale_xyz = (frame['scale']['x'], frame['scale']['y'], frame['scale']['z'])

                matrix.put_rotation(rotation_xyz, frame['rotation']['w'])
                matrix.put_position(position_xyz)
                matrix.put_scale(scale_xyz)

                matrix = matrix.translation_matrix @ matrix.rotation_matrix @ matrix.scale_matrix
                matrix_values = []
                for row in matrix.matrix:
                    for column in row:
                        matrix_values.append(str(column))

                if node_data['frames'].index(frame) == 0:
                    SubElement(node, 'matrix', sid='transform').text = ' '.join(matrix_values)
                matrix_output.append(' '.join(matrix_values))

            if len(frames) > 1:
                animation = SubElement(library_animations, 'animation', id=node_name)

                dae.write_source(
                    animation,
                    f'{node_name}-time-input',
                    'float_array',
                    time_input,
                    1,
                    [{'name': 'TIME', 'type': 'float'}]
                )
                dae.write_source(
                    animation,
                    f'{node_name}-matrix-output',
                    'float_array',
                    matrix_output,
                    16,
                    [{'name': 'TRANSFORM', 'type': 'float4x4'}]
                )
                dae.write_source(
                    animation,
                    f'{node_name}-interpolation',
                    'Name_array',
                    ['LINEAR'] * len(frames),
                    1,
                    [{'name': 'INTERPOLATION', 'type': 'name'}]
                )

                sampler = SubElement(animation, 'sampler', id=f'{node_name}-sampler')

                dae.write_input(
                    sampler,
                    'INPUT',
                    f'{node_name}-time-input'
                )

                dae.write_input(
                    sampler,
                    'OUTPUT',
                    f'{node_name}-matrix-output'
                )

                dae.write_input(
                    sampler,
                    'INTERPOLATION',
                    f'{node_name}-interpolation'
                )

                SubElement(animation, 'channel',
                           source=f'#{node_name}-sampler',
                           target=f'{node_name}/transform')

        scene = SubElement(dae.collada, 'scene')
        SubElement(scene, 'instance_visual_scene',
                   url='#3dConverterScene',
                   name='3d-Converter Scene')

        # </Scene>

        self.writen = tostring(dae.collada, xml_declaration=True).decode()


class Parser:
    def node(self, nodes):
        nodes_list = []
        for node in nodes:
            instance_geometry = node.findall('collada:instance_geometry', self.namespaces)
            instance_controller = node.findall('collada:instance_controller', self.namespaces)

            instances = instance_geometry.extend(instance_controller)

            children = self.node(node.findall('collada:node', self.namespaces))

            if 'name' not in node.attrib:
                node.attrib['name'] = node.attrib['id']

            node_data = {
                'name': node.attrib['name'],
                'instances': []
            }

            for instance in instances:
                node_data['instances'] = [{}]
                binds = []

                bind_material = instance.find('collada:bind_material', self.namespaces)
                technique_common = bind_material[0]

                for instance_material in technique_common:
                    binds.append({
                        'symbol': instance_material.attrib['symbol'],
                        'target': instance_material.attrib['target'][1:]
                    })

                if instance_geometry:
                    node_data['instances'][0]['instance_type'] = 'GEOM'

                    geometry_url = instance_geometry.attrib['url']
                    node_data['instances'][0]['instance_name'] = geometry_url[1:]
                elif instance_controller:
                    node_data['instances'][0]['instance_type'] = 'CONT'

                    controller_url = instance_controller.attrib['url']
                    node_data['instances'][0]['instance_name'] = controller_url[1:]

                node_data['instances'][len(node_data['instances'])-1]['binds'] = binds

            matrix = node.findall('collada:matrix', self.namespaces)
            if matrix:
                matrix_data = matrix[0].text.split()
                matrix_data = [[float(value) for value in matrix_data[x:x + 4]] for x in range(0, len(matrix_data), 4)]

                node_data['matrix'] = matrix_data

            node_data['children'] = children

            nodes_list.append(node_data)

        return nodes_list

    def fix_nodes_list(self, nodes, parent: str = ''):
        for node in nodes:
            node_data = {
                'name': node['name'],
                'parent': parent,
                'instances': node['instances']
            }

            if len(node_data['instances']) == 0:
                node_data['frames_settings'] = [0, 0, 0, 0, 0, 0, 0, 0]
                node_data['frames'] = []

                if 'matrix' in node:
                    matrix = Matrix4x4(matrix=node['matrix'])

                    # scale = matrix.get_scale()
                    position = matrix.get_position()

                    node_data['frames'] = [
                        {
                            'frame_id': 0,
                            'rotation': {'x': 0, 'y': 0, 'z': 0, 'w': 0},
                            'position': position,
                            'scale': {'x': 1, 'y': 1, 'z': 1}
                        }
                    ]
            else:
                node_data['frames'] = []

            # node_data['frames'] = node['frames']
            self.parsed['nodes'].append(node_data)
            self.fix_nodes_list(node['children'], node['name'])

    def __init__(self, file_data):
        self.parsed = {'header': {'version': 2,
                                  'frame_rate': 30,
                                  'materials_file': 'sc3d/character_materials.scw'},
                       'materials': [],
                       'geometries': [],
                       'cameras': [],
                       'nodes': []}

        self.geometry_info = {}

        root = fromstring(file_data)

        self.namespaces = {
            'collada': 'http://www.collada.org/2005/11/COLLADASchema'
        }

        # <Libraries>
        self.library_materials = root.find('./collada:library_materials', self.namespaces)
        self.library_effects = root.find('./collada:library_effects', self.namespaces)

        self.library_geometries = root.find('./collada:library_geometries', self.namespaces)
        self.library_controllers = root.find('./collada:library_controllers', self.namespaces)

        self.instance_scene = root.find('./collada:scene', self.namespaces).find('collada:instance_visual_scene',
                                                                                 self.namespaces)
        self.library_scenes = root.find('./collada:library_visual_scenes', self.namespaces)
        # </Libraries>

        if self.library_materials is None:
            self.library_materials = []

    def parse(self):
        for material in self.library_materials:
            material_name = material.attrib['name']

            instance_effect = material.find('collada:instance_effect', self.namespaces)
            if instance_effect is not None:
                effect_url = instance_effect.attrib['url'][1:]
                effect = self.library_effects.find(f'collada:effect[@id="{effect_url}"]', self.namespaces)

                if effect is not None:
                    profile = None
                    for item in effect:
                        if 'profile' in item.tag:
                            profile = item
                    technique = profile.find('collada:technique', self.namespaces)

                    emission_data = None
                    ambient_data = None
                    diffuse_data = None

                    emission = technique[0].find('collada:emission', self.namespaces)
                    ambient = technique[0].find('collada:ambient', self.namespaces)
                    diffuse = technique[0].find('collada:diffuse', self.namespaces)

                    if 'color' in emission[0].tag:
                        emission_data = [float(item) for item in emission[0].text.split()]
                        emission_data[3] *= 255
                    elif 'texture' in emission[0].tag:
                        # emission_data = emission[0].attrib['texture']
                        emission_data = '.'

                    if 'color' in ambient[0].tag:
                        ambient_data = [float(item) for item in ambient[0].text.split()]
                        ambient_data[3] *= 255
                    elif 'texture' in ambient[0].tag:
                        # ambient_data = ambient[0].attrib['texture']
                        ambient_data = '.'

                    if 'color' in diffuse[0].tag:
                        diffuse_data = [float(item) for item in diffuse[0].text.split()]
                        diffuse_data[3] *= 255
                    elif 'texture' in diffuse[0].tag:
                        # diffuse_data = diffuse[0].attrib['texture']
                        diffuse_data = '.'

                    material_data = {
                        'name': material_name,
                        'effect': {
                            'ambient': ambient_data,
                            'diffuse': diffuse_data,
                            'specular': '.',
                            'colorize': [255, 255, 255, 255],
                            'emission': emission_data,
                            'lightmaps': {
                                'diffuse': 'sc3d/diffuse_lightmap.png',
                                'specular': 'sc3d/specular_lightmap.png'
                            },
                            'tint': [0, 0, 0, 0]
                        }
                    }

                    self.parsed['materials'].append(material_data)

        scene_url = self.instance_scene.attrib['url'][1:]
        scene = self.library_scenes.find(f'collada:visual_scene[@id="{scene_url}"]', self.namespaces)

        nodes = self.node(scene.findall('collada:node', self.namespaces))
        self.fix_nodes_list(nodes)
        self.parse_nodes()

    def parse_nodes(self):
        nodes = self.parsed['nodes']
        for node_index in range(len(nodes)):
            node = nodes[node_index]
            for instance in node['instances']:
                controller = None
                geometry = None

                if node['instance_type'] == 'CONT':
                    controller = self.library_controllers \
                        .find(f'collada:controller[@id="{instance["instance_name"]}"]', self.namespaces)

                    geometry_url = controller[0].attrib['source'][1:]
                    geometry = self.library_geometries \
                        .find(f'collada:geometry[@id="{geometry_url}"]', self.namespaces)
                elif node['instance_type'] == 'GEOM':
                    geometry = self.library_geometries \
                        .find(f'collada:geometry[@id="{instance["instance_name"]}"]', self.namespaces)

                node['instance_name'] = geometry.attrib['name']

                for suffix in ['-skin', '-cont']:
                    node['instance_name'] = node['instance_name'].removesuffix(suffix)
                for suffix in ['-mesh', '-geom']:
                    node['instance_name'] = node['instance_name'].removesuffix(suffix)

                self.parsed['nodes'][node_index] = node

                if geometry is not None:
                    self.geometry_info = {'name': '',
                                          'group': node['parent'],
                                          'vertices': [],
                                          'have_bind_matrix': False,
                                          'materials': []}
                    if controller is not None:
                        self.parse_controller(controller)

                    self.parse_geometry(geometry)

    def parse_controller(self, controller):
        self.geometry_info['have_bind_matrix'] = True

        skin = controller[0]

        bind_shape_matrix = skin.find('collada:bind_shape_matrix', self.namespaces).text
        bind_shape_matrix = [float(x) for x in bind_shape_matrix.split()]

        self.geometry_info['bind_matrix'] = bind_shape_matrix

        self.geometry_info['joints'] = []
        joints = skin.find('collada:joints', self.namespaces)
        joint_inputs = joints.findall('collada:input', self.namespaces)
        for _input in joint_inputs:
            # semantic = _input.attrib['semantic']
            source_url = _input.attrib['source']
            source = skin.find(f'collada:source[@id="{source_url[1:]}"]', self.namespaces)

            accessor = source.find('collada:technique_common/collada:accessor', self.namespaces)
            accessor_stride = int(accessor.attrib['stride'])
            accessor_source_url = accessor.attrib['source']
            accessor_source = source.find(f'collada:*[@id="{accessor_source_url[1:]}"]', self.namespaces)
            params = accessor.findall('collada:param', self.namespaces)

            for param in params:
                param_name = param.attrib['name']
                # param_type = param.attrib['type']

                if param_name == 'JOINT':
                    for name in accessor_source.text.split():
                        self.geometry_info['joints'].append({
                            'name': name
                        })

                if param_name == 'TRANSFORM':
                    for x in range(int(accessor_source.attrib['count']) // int(accessor_stride)):
                        matrix = []
                        for y in accessor_source.text.split()[x * accessor_stride:(x + 1) * accessor_stride]:
                            matrix.append(float(y))
                        self.geometry_info['joints'][x]['matrix'] = matrix

        self.geometry_info['weights'] = {}
        vertex_weights = skin.find('collada:vertex_weights', self.namespaces)
        vertex_weights_inputs = vertex_weights.findall('collada:input', self.namespaces)
        for _input in vertex_weights_inputs:
            semantic = _input.attrib['semantic']
            source_url = _input.attrib['source']
            source = skin.find(f'collada:source[@id="{source_url[1:]}"]', self.namespaces)

            if semantic == 'WEIGHT':
                accessor = source.find('collada:technique_common/collada:accessor', self.namespaces)
                accessor_source_url = accessor.attrib['source']
                accessor_source = source.find(f'collada:*[@id="{accessor_source_url[1:]}"]', self.namespaces)

                params = accessor.findall('collada:param', self.namespaces)
                for param in params:
                    param_name = param.attrib['name']
                    # param_type = param.attrib['type']

                    if param_name == 'WEIGHT':
                        weights = [float(x) for x in accessor_source.text.split()]
                        self.geometry_info['weights']['weights'] = weights

            vcount = vertex_weights.find('collada:vcount', self.namespaces).text
            vcount = [int(x) for x in vcount.split()]
            self.geometry_info['weights']['vcount'] = vcount

            v = vertex_weights.find('collada:v', self.namespaces).text
            v = [int(x) for x in v.split()]
            self.geometry_info['weights']['vertex_weights'] = v

    def parse_geometry(self, geometry):
        name = geometry.attrib['name']

        if name[-5:] in ['-mesh', '-geom']:
            name = name[:-5]

        self.geometry_info['name'] = name

        mesh = geometry[0]

        triangles = mesh.findall('collada:triangles', self.namespaces)
        if triangles:
            pass
        else:
            triangles = mesh.findall('collada:polylist', self.namespaces)
        inputs = triangles[0].findall('collada:input', self.namespaces)
        for _input in inputs:
            semantic = _input.attrib['semantic']
            source_link = _input.attrib['source'][1:]
            source = mesh.find(f'*[@id="{source_link}"]')

            if semantic == 'VERTEX':
                vertices_input = source[0]
                semantic = vertices_input.attrib['semantic']
                source_link = vertices_input.attrib['source'][1:]
                source = mesh.find(f'*[@id="{source_link}"]')

            float_array = source.find('collada:float_array', self.namespaces)
            accessor = source.find('collada:technique_common/collada:accessor', self.namespaces)

            vertex_temp = [float(floating) for floating in float_array.text.split()]

            scale = max(max(vertex_temp), abs(min(vertex_temp)))
            if scale < 1:
                scale = 1
            if semantic == 'TEXCOORD':
                vertex_temp[1::2] = [1 - x for x in vertex_temp[1::2]]
            vertex_temp = [value / scale for value in vertex_temp]

            vertex = []
            for x in range(0, len(vertex_temp), len(accessor)):
                vertex.append(vertex_temp[x: x + len(accessor)])

            self.geometry_info['vertices'].append({'type': semantic,
                                                   'index': 0,
                                                   'scale': scale,
                                                   'vertex': vertex})
        for triangle in triangles:
            triangles_material = triangle.attrib['material']

            p = triangle.find('collada:p', self.namespaces)
            polygons_temp = [int(integer) for integer in p.text.split()]

            polygons = []
            for x in range(0, len(polygons_temp), len(inputs) * 3):
                temp_list = []
                for x1 in range(len(inputs)):
                    second_temp_list = []
                    for x2 in range(3):
                        second_temp_list.append(polygons_temp[x + x1 + x2])
                    temp_list.append(second_temp_list)
                polygons.append(temp_list)
            self.geometry_info['materials'].append({'name': triangles_material,
                                                    'polygons': polygons})
        self.parsed['geometries'].append(self.geometry_info)
