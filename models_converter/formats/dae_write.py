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
        library_images = SubElement(dae.collada, 'library_images')
        library_geometries = SubElement(dae.collada, 'library_geometries')
        library_controllers = SubElement(dae.collada, 'library_controllers')
        library_animations = SubElement(dae.collada, 'library_animations')
        library_cameras = SubElement(dae.collada, 'library_cameras')
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

            if node_data['has_target']:
                target_type = node_data['target_type']
                target_id = node_data['target']

                if target_type == 'CONT':
                    instance_controller = SubElement(node, 'instance_controller', url=f'#{target_id}-cont')
                    bind_material = SubElement(instance_controller, 'bind_material')
                    technique_common = SubElement(bind_material, 'technique_common')
                    for bind in node_data['binds']:
                        symbol = bind['symbol']
                        target = bind['target']

                        SubElement(technique_common, 'instance_material',
                                   symbol=symbol,
                                   target=f'#{target}')
                elif target_type == 'GEOM':
                    instance_controller = SubElement(node, 'instance_geometry', url=f'#{target_id}-geom')
                    bind_material = SubElement(instance_controller, 'bind_material')
                    technique_common = SubElement(bind_material, 'technique_common')
                    for bind in node_data['binds']:
                        symbol = bind['symbol']
                        target = bind['target']

                        SubElement(technique_common, 'instance_material',
                                   symbol=symbol,
                                   target=f'#{target}')
            else:
                if parent_name != '':
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
