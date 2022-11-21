from xml.etree.ElementTree import *

from .collada import Collada
from ..universal import Scene, Node, Geometry
from ...interfaces import WriterInterface
from ...utilities.matrix.matrix4x4 import Matrix4x4


class Writer(WriterInterface):
    def __init__(self):
        self.writen = None
        self.dae = Collada()

        self.library_materials = None
        self.library_effects = None
        self.library_images = None
        self.library_geometries = None
        self.library_controllers = None
        self.library_animations = None
        self.library_cameras = None
        self.library_visual_scenes = None

    def create_libraries(self):
        self.library_materials = SubElement(self.dae.root, 'library_materials')
        self.library_effects = SubElement(self.dae.root, 'library_effects')
        # self.library_images = SubElement(dae.collada, 'library_images')
        self.library_geometries = SubElement(self.dae.root, 'library_geometries')
        self.library_controllers = SubElement(self.dae.root, 'library_controllers')
        self.library_animations = SubElement(self.dae.root, 'library_animations')
        # self.library_cameras = SubElement(self.dae.collada, 'library_cameras')
        self.library_visual_scenes = SubElement(self.dae.root, 'library_visual_scenes')

    def sign(self):
        asset = SubElement(self.dae.root, 'asset')

        contributor = SubElement(asset, 'contributor')
        SubElement(contributor, 'author').text = 'Vorono4ka'
        SubElement(contributor, 'authoring_tool').text = 'models_converter (https://github.com/vorono4ka/3d-converter)'

        return contributor

    def write(self, scene: Scene):
        contributor = self.sign()

        # if 'version' in data['header']:
        #     SubElement(contributor, 'comments').text = 'Version: ' + str(data['header']['version'])

        self.create_libraries()

        # for material in scene.get_materials():
        #     self.create_material(material)

        for geometry in scene.get_geometries():
            geometry_name = self.create_geometry(geometry)

            if geometry.has_controller():
                self.create_controller(geometry_name, geometry)

        self.create_scene(scene)

        self.writen = tostring(self.dae.root, xml_declaration=True).decode()

    def create_material(self, material_data):
        material_name = material_data['name']
        SubElement(self.library_materials, 'material', id=material_name)
        effect_name = f'{material_name}-effect'
        material = SubElement(self.library_materials, 'material', id=material_name)
        SubElement(material, 'instance_effect', url=f'#{effect_name}')
        effect = SubElement(self.library_effects, 'effect', id=effect_name)
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

    def create_geometry(self, geometry: Geometry):
        geometry_name = geometry.get_name()
        collada_geometry = SubElement(self.library_geometries, 'geometry', id=f'{geometry_name}-geom')
        mesh = SubElement(collada_geometry, 'mesh')

        for vertex in geometry.get_vertices():
            params = []

            vertex_type = vertex.get_type()
            vertex_name = vertex.get_name()
            coordinate = vertex.get_points()
            stride = len(coordinate[0])

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

            self.dae.write_source(
                mesh,
                source_name,
                'float_array',
                tuple(' '.join(str(sub_item * vertex.get_scale()) for sub_item in item) for item in coordinate),
                stride,
                params
            )

            if vertex_type == 'POSITION':
                vertices = SubElement(mesh, 'vertices', id=f'{source_name}-vertices')
                self.dae.write_input(vertices, 'POSITION', source_name)
        for material in geometry.get_materials():
            collada_triangles = SubElement(mesh, 'triangles',
                                           count=f'{len(material.get_triangles())}',
                                           material=material.get_name())

            for vertex in material.get_input_vertices():
                input_type = vertex.get_type()
                if input_type == 'POSITION':
                    input_type = 'VERTEX'

                source_id = f'{geometry_name}-{vertex.get_name()}'
                if input_type == 'VERTEX':
                    source_id = f'{source_id}-vertices'

                self.dae.write_input(collada_triangles, input_type, source_id, vertex.get_index())
            polygons = SubElement(collada_triangles, 'p')

            formatted_polygons_data = []
            for triangle in material.get_triangles():
                for point in triangle:
                    for coordinate in point:
                        formatted_polygons_data.append(str(coordinate))

            polygons.text = ' '.join(formatted_polygons_data)
        return geometry_name

    def create_controller(self, geometry_name: str, geometry: Geometry):
        controller = SubElement(self.library_controllers, 'controller', id=f'{geometry_name}-cont')
        skin = SubElement(controller, 'skin', source=f'#{geometry_name}-geom')

        SubElement(skin, 'bind_shape_matrix').text = ' '.join(map(str, geometry.get_bind_matrix()))

        joints_names_source_id = f'{geometry_name}-joints'
        joints_matrices_source_id = f'{geometry_name}-joints-bind-matrices'
        weights_source_id = f'{geometry_name}-weights'

        self.dae.write_source(
            skin,
            joints_names_source_id,
            'Name_array',
            tuple(joint.get_name() for joint in geometry.get_joints()),
            1,
            [{'name': 'JOINT', 'type': 'name'}]
        )

        self.dae.write_source(
            skin,
            joints_matrices_source_id,
            'float_array',
            tuple(' '.join(map(str, joint.get_matrix())) for joint in geometry.get_joints()),
            16,
            [{'name': 'TRANSFORM', 'type': 'float4x4'}]
        )

        vertex_weights = []
        unique_weights = []
        vcount = [0] * (len(geometry.get_weights()) // 4)

        for weight_index in range(len(geometry.get_weights())):
            weight = geometry.get_weights()[weight_index]
            if weight.get_strength() == 0:
                continue

            vcount[weight_index // 4] += 1
            vertex_weights.append(weight.get_joint_index())
            if weight.get_strength() in unique_weights:
                vertex_weights.append(unique_weights.index(weight.get_strength()))
            else:
                unique_weights.append(weight.get_strength())
                vertex_weights.append(len(unique_weights) - 1)

        self.dae.write_source(
            skin,
            weights_source_id,
            'float_array',
            tuple(map(str, unique_weights)),
            1,
            [{'name': 'WEIGHT', 'type': 'float'}]
        )

        joints = SubElement(skin, 'joints')
        self.dae.write_input(joints, 'JOINT', joints_names_source_id)
        self.dae.write_input(joints, 'INV_BIND_MATRIX', joints_matrices_source_id)

        collada_vertex_weights = SubElement(skin, 'vertex_weights', count=f'{len(vcount)}')
        self.dae.write_input(collada_vertex_weights, 'JOINT', joints_names_source_id, 0)
        self.dae.write_input(collada_vertex_weights, 'WEIGHT', weights_source_id, 1)

        SubElement(collada_vertex_weights, 'vcount').text = ' '.join(map(str, vcount))
        SubElement(collada_vertex_weights, 'v').text = ' '.join(map(str, vertex_weights))

    def create_animation(self, node_name, frames, matrix_output, time_input):
        animation = SubElement(self.library_animations, 'animation', id=node_name)

        self.dae.write_source(
            animation,
            f'{node_name}-time-input',
            'float_array',
            time_input,
            1,
            [{'name': 'TIME', 'type': 'float'}]
        )

        self.dae.write_source(
            animation,
            f'{node_name}-matrix-output',
            'float_array',
            matrix_output,
            16,
            [{'name': 'TRANSFORM', 'type': 'float4x4'}]
        )

        self.dae.write_source(
            animation,
            f'{node_name}-interpolation',
            'Name_array',
            tuple('LINEAR' for _ in range(len(frames))),
            1,
            [{'name': 'INTERPOLATION', 'type': 'name'}]
        )

        sampler = SubElement(animation, 'sampler', id=f'{node_name}-sampler')

        self.dae.write_input(
            sampler,
            'INPUT',
            f'{node_name}-time-input'
        )

        self.dae.write_input(
            sampler,
            'OUTPUT',
            f'{node_name}-matrix-output'
        )

        self.dae.write_input(
            sampler,
            'INTERPOLATION',
            f'{node_name}-interpolation'
        )

        SubElement(animation, 'channel',
                   source=f'#{node_name}-sampler',
                   target=f'{node_name}/transform')

    def create_scene(self, scene: Scene):
        visual_scene = SubElement(self.library_visual_scenes, 'visual_scene',
                                  id='3dConverterScene',
                                  name='3d-Converter Scene')
        not_joint_nodes = []
        node_index = 0
        parent_name = None
        while node_index < len(not_joint_nodes) or len(not_joint_nodes) == 0:
            if len(not_joint_nodes) > 0:
                parent_name = not_joint_nodes[node_index]

            for _node in scene.get_nodes():
                if _node.get_instances() or _node.get_name() == parent_name:
                    if not (_node.get_name() in not_joint_nodes):
                        not_joint_nodes.append(_node.get_name())
                    if not (_node.get_parent() in not_joint_nodes):
                        not_joint_nodes.append(_node.get_parent())
            node_index += 1
        for node in scene.get_nodes():
            self.create_node(visual_scene, node, scene, not_joint_nodes)

        collada_scene = SubElement(self.dae.root, 'scene')
        SubElement(collada_scene, 'instance_visual_scene',
                   url='#3dConverterScene',
                   name='3d-Converter Scene')

    def create_node(self, visual_scene, node: Node, scene: Scene, not_joint_nodes):
        parent_name = node.get_parent()
        parent = visual_scene
        if parent_name != '':
            parent = visual_scene.find(f'.//*[@id="{parent_name}"]')
            if parent is None:
                parent = visual_scene
        node_name = node.get_name()
        collada_node = SubElement(parent, 'node', id=node.get_name())
        for instance in node.get_instances():
            bind_material = None

            instance_type = instance.get_type()
            if instance_type == 'CONT':
                instance_controller = SubElement(collada_node, 'instance_controller',
                                                 url=f'#{instance.get_name()}-cont')
                bind_material = SubElement(instance_controller, 'bind_material')
            elif instance_type == 'GEOM':
                instance_controller = SubElement(collada_node, 'instance_geometry', url=f'#{instance.get_name()}-geom')
                bind_material = SubElement(instance_controller, 'bind_material')

            if instance_type in ['GEOM', 'CONT']:
                technique_common = SubElement(bind_material, 'technique_common')
                for bind in instance.get_binds():
                    SubElement(technique_common, 'instance_material',
                               symbol=bind.get_symbol(),
                               target=f'#{bind.get_target()}')
        else:
            if not (node.get_name() in not_joint_nodes):
                collada_node.attrib['type'] = 'JOINT'

        time_input = []
        matrix_output = []
        for frame_index in range(len(node.get_frames())):
            frame = node.get_frames()[frame_index]
            frame_id = frame.get_id()
            matrix = Matrix4x4()

            time_input.append(str(frame_id / scene.get_frame_rate()))

            rotation_matrix = matrix.create_rotation_matrix(frame.get_rotation())
            translation_matrix = matrix.create_translation_matrix(frame.get_position())
            scale_matrix = matrix.create_scale_matrix(frame.get_scale())

            matrix = translation_matrix @ rotation_matrix @ scale_matrix
            matrix_values = []
            for row in matrix.matrix:
                for column in row:
                    matrix_values.append(str(column))

            if frame_index == 0:
                SubElement(collada_node, 'matrix', sid='transform').text = ' '.join(matrix_values)
            matrix_output.append(' '.join(matrix_values))

        if len(node.get_frames()) > 1:
            self.create_animation(node_name, node.get_frames(), matrix_output, time_input)
