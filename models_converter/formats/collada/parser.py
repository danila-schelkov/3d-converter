from xml.etree.ElementTree import *

from .collada import NAMESPACE
from ..universal import Node, Scene, Geometry
from ...interfaces import ParserInterface
from ...utilities import remove_suffix
from ...utilities.matrix.matrix4x4 import Matrix4x4

NAMESPACES = {
    'collada': NAMESPACE
}


class Parser(ParserInterface):
    def __init__(self, file_data):
        self.library_materials = None
        self.library_effects = None
        self.library_geometries = None
        self.library_controllers = None
        self.instance_scene = None
        self.library_scenes = None

        self.scene = Scene()

        root = fromstring(file_data)

        self.find_libraries(root)

        self.instance_scene = root.find('./collada:scene', NAMESPACES).find('collada:instance_visual_scene', NAMESPACES)

    def find_libraries(self, root):
        self.library_materials = root.find('./collada:library_materials', NAMESPACES)
        if self.library_materials is None:
            self.library_materials = []

        self.library_effects = root.find('./collada:library_effects', NAMESPACES)
        self.library_geometries = root.find('./collada:library_geometries', NAMESPACES)
        self.library_controllers = root.find('./collada:library_controllers', NAMESPACES)
        self.library_scenes = root.find('./collada:library_visual_scenes', NAMESPACES)

    def parse(self):
        self.parse_materials()

        scene_url = self.instance_scene.attrib['url'][1:]
        scene = self.library_scenes.find(f'collada:visual_scene[@id="{scene_url}"]', NAMESPACES)

        self.parse_node(scene.findall('collada:node', NAMESPACES))
        self.parse_nodes()

    def parse_materials(self):
        for material in self.library_materials:
            material_name = material.attrib['name']

            instance_effect = material.find('collada:instance_effect', NAMESPACES)
            if instance_effect is not None:
                effect_url = instance_effect.attrib['url'][1:]
                effect = self.library_effects.find(f'collada:effect[@id="{effect_url}"]', NAMESPACES)

                if effect is not None:
                    # profile = None
                    # for item in effect:
                    #     if 'profile' in item.tag:
                    #         profile = item
                    # technique = profile.find('collada:technique', NAMESPACES)
                    #
                    # emission_data = None
                    # ambient_data = None
                    # diffuse_data = None
                    #
                    # emission = technique[0].find('collada:emission', NAMESPACES)
                    # ambient = technique[0].find('collada:ambient', NAMESPACES)
                    # diffuse = technique[0].find('collada:diffuse', NAMESPACES)
                    #
                    # if 'color' in emission[0].tag:
                    #     emission_data = [float(item) for item in emission[0].text.split()]
                    #     emission_data[3] *= 255
                    # elif 'texture' in emission[0].tag:
                    #     # emission_data = emission[0].attrib['texture']
                    #     emission_data = '.'
                    #
                    # if 'color' in ambient[0].tag:
                    #     ambient_data = [float(item) for item in ambient[0].text.split()]
                    #     ambient_data[3] *= 255
                    # elif 'texture' in ambient[0].tag:
                    #     # ambient_data = ambient[0].attrib['texture']
                    #     ambient_data = '.'
                    #
                    # if 'color' in diffuse[0].tag:
                    #     diffuse_data = [float(item) for item in diffuse[0].text.split()]
                    #     diffuse_data[3] *= 255
                    # elif 'texture' in diffuse[0].tag:
                    #     # diffuse_data = diffuse[0].attrib['texture']
                    #     diffuse_data = '.'

                    material_data = {
                        'name': material_name,
                        'shader': 'shader/uber.vsh',
                        'effect': {
                            'ambient': [0, 0, 0, 255],  # ambient_data,
                            'diffuse': '.',  # diffuse_data,
                            'specular': '.',
                            'colorize': [255, 255, 255, 255],
                            'emission': [0, 0, 0, 255],  # emission_data,
                            'lightmaps': {
                                'diffuse': 'sc3d/diffuse_lightmap.png',
                                'specular': 'sc3d/specular_lightmap.png'
                            },
                            'shader_define_flags': 3014
                        }
                    }

                    self.scene.add_material(material_data)

    def parse_node(self, xml_nodes: list, parent: str = None):
        for xml_node in xml_nodes:
            if not ('name' in xml_node.attrib):
                xml_node.attrib['name'] = xml_node.attrib['id']

            node: Node = Node(
                name=xml_node.attrib['name'],
                parent=parent
            )

            instance_geometry = xml_node.findall('collada:instance_geometry', NAMESPACES)
            instance_controller = xml_node.findall('collada:instance_controller', NAMESPACES)

            for xml_instance in [*instance_geometry, *instance_controller]:
                if instance_geometry:
                    instance = Node.Instance(name=xml_instance.attrib['url'][1:], instance_type='GEOM')
                elif instance_controller:
                    instance = Node.Instance(name=xml_instance.attrib['url'][1:], instance_type='CONT')
                else:
                    continue

                bind_material = xml_instance.find('collada:bind_material', NAMESPACES)

                technique_common = bind_material[0]
                for instance_material in technique_common:
                    instance.add_bind(instance_material.attrib['symbol'], instance_material.attrib['target'][1:])

                node.add_instance(instance)

            xml_matrix = xml_node.findall('collada:matrix', NAMESPACES)
            if xml_matrix:
                matrix = xml_matrix[0].text.split()
                matrix = [[float(value) for value in matrix[x:x + 4]] for x in range(0, len(matrix), 4)]

                matrix = Matrix4x4(matrix=matrix)

                scale = matrix.get_scale()
                position = matrix.get_position()
                rotation = matrix.get_rotation()

                node.add_frame(Node.Frame(0, position, scale, rotation))

            self.scene.add_node(node)
            self.parse_node(xml_node.findall('collada:node', NAMESPACES), node.get_name())

    def parse_nodes(self):
        nodes = self.scene.get_nodes()
        for node_index in range(len(nodes)):
            node = nodes[node_index]
            for instance in node.get_instances():
                controller = None
                collada_geometry = None

                if instance.get_type() == 'CONT':
                    controller = self.library_controllers.find(f'collada:controller[@id="{instance.get_name()}"]',
                                                               NAMESPACES)
                    geometry_url = controller[0].attrib['source'][1:]
                    collada_geometry = self.library_geometries.find(f'collada:geometry[@id="{geometry_url}"]',
                                                                    NAMESPACES)
                elif instance.get_type() == 'GEOM':
                    collada_geometry = self.library_geometries.find(f'collada:geometry[@id="{instance.get_name()}"]',
                                                                    NAMESPACES)

                if not ('name' in collada_geometry.attrib):
                    collada_geometry.attrib['name'] = collada_geometry.attrib['id']

                instance._name = collada_geometry.attrib['name']

                for suffix in ('-skin', '-cont'):
                    instance._name = remove_suffix(instance.get_name(), suffix)
                for suffix in ('-mesh', '-geom'):
                    instance._name = remove_suffix(instance.get_name(), suffix)

                if collada_geometry is not None:
                    geometry = self.parse_geometry(collada_geometry)
                    if controller is not None:
                        self.parse_controller(controller, geometry)

    def parse_controller(self, collada_controller, geometry: Geometry):
        skin = collada_controller[0]

        bind_shape_matrix = skin.find('collada:bind_shape_matrix', NAMESPACES).text

        geometry.set_controller_bind_matrix(list(map(float, bind_shape_matrix.split())))

        joints = skin.find('collada:joints', NAMESPACES)
        joint_inputs = joints.findall('collada:input', NAMESPACES)
        for _input in joint_inputs:
            # semantic = _input.attrib['semantic']
            source_url = _input.attrib['source']
            source = skin.find(f'collada:source[@id="{source_url[1:]}"]', NAMESPACES)

            accessor = source.find('collada:technique_common/collada:accessor', NAMESPACES)
            accessor_stride = int(accessor.attrib['stride'])
            accessor_source_url = accessor.attrib['source']
            accessor_source = source.find(f'collada:*[@id="{accessor_source_url[1:]}"]', NAMESPACES)
            params = accessor.findall('collada:param', NAMESPACES)

            for param in params:
                param_name = param.attrib['name']
                # param_type = param.attrib['type']

                source_data = accessor_source.text.split()
                if param_name == 'JOINT':
                    for name in source_data:
                        geometry.add_joint(Geometry.Joint(name, None))

                if param_name == 'TRANSFORM':
                    for x in range(int(accessor_source.attrib['count']) // int(accessor_stride)):
                        matrix = []
                        for y in source_data[x * accessor_stride:(x + 1) * accessor_stride]:
                            matrix.append(float(y))
                        geometry.get_joints()[x].set_matrix(matrix)

        vertex_weights = skin.find('collada:vertex_weights', NAMESPACES)
        vertex_weights_inputs = vertex_weights.findall('collada:input', NAMESPACES)
        for _input in vertex_weights_inputs:
            semantic = _input.attrib['semantic']
            source_url = _input.attrib['source']
            source = skin.find(f'collada:source[@id="{source_url[1:]}"]', NAMESPACES)

            if semantic == 'WEIGHT':
                accessor = source.find('collada:technique_common/collada:accessor', NAMESPACES)
                accessor_source_url = accessor.attrib['source']
                accessor_source = source.find(f'collada:*[@id="{accessor_source_url[1:]}"]', NAMESPACES)

                weights = None
                params = accessor.findall('collada:param', NAMESPACES)
                for param in params:
                    param_name = param.attrib['name']
                    # param_type = param.attrib['type']

                    if param_name == 'WEIGHT':
                        weights = [float(x) for x in accessor_source.text.split()]
                        break

                if weights is None:
                    continue

                vcount = vertex_weights.find('collada:vcount', NAMESPACES).text

                v = vertex_weights.find('collada:v', NAMESPACES).text
                v = map(int, v.split())

                for count in map(int, vcount.split()):
                    for i in range(count):
                        joint_index = next(v)
                        strength_index = next(v)
                        geometry.add_weight(Geometry.Weight(joint_index, weights[strength_index]))

                    while count < 4:
                        geometry.add_weight(Geometry.Weight(0, 0))
                        count += 1
                break

    def parse_geometry(self, collada_geometry) -> Geometry:
        name = collada_geometry.attrib['name']

        for suffix in ('-mesh', '-geom'):
            name = remove_suffix(name, suffix)

        geometry = Geometry(name=name, group='GEO')

        mesh = collada_geometry[0]

        triangles = mesh.findall('collada:triangles', NAMESPACES)
        if triangles:
            pass
        else:
            triangles = mesh.findall('collada:polylist', NAMESPACES)

        vertices_inputs = []
        inputs = triangles[0].findall('collada:input', NAMESPACES)
        for _input in inputs:
            semantic = _input.attrib['semantic']
            source_link = _input.attrib['source'][1:]
            source = mesh.find(f'*[@id="{source_link}"]')

            if semantic == 'VERTEX':
                vertices_input = source[0]
                semantic = vertices_input.attrib['semantic']
                source_link = vertices_input.attrib['source'][1:]
                source = mesh.find(f'*[@id="{source_link}"]')

            float_array = source.find('collada:float_array', NAMESPACES)
            accessor = source.find('collada:technique_common/collada:accessor', NAMESPACES)

            points_temp = [float(floating) for floating in float_array.text.split()]

            scale = max(max(points_temp), abs(min(points_temp)))
            if scale < 1:
                scale = 1
            if semantic == 'TEXCOORD':
                points_temp[1::2] = [1 - x for x in points_temp[1::2]]
            points_temp = [value / scale for value in points_temp]

            points = []
            for x in range(0, len(points_temp), len(accessor)):
                points.append(points_temp[x: x + len(accessor)])

            vertex = Geometry.Vertex(
                name=source_link,
                vertex_type=semantic,
                vertex_index=len(geometry.get_vertices()),
                vertex_scale=scale,
                points=points
            )

            vertices_inputs.append(vertex)
            geometry.add_vertex(vertex)
        for triangle in triangles:
            triangles_material = triangle.attrib['material']

            p = triangle.find('collada:p', NAMESPACES)
            triangles_temp = [int(integer) for integer in p.text.split()]

            triangles = [
                [
                    triangles_temp[polygon_index + point_index:polygon_index + point_index + 3]
                    for point_index in range(0, len(inputs) * 3, 3)
                ] for polygon_index in range(0, len(triangles_temp), len(inputs) * 3)
            ]
            geometry.add_material(Geometry.Material(
                name=triangles_material,
                triangles=triangles,
                input_vertices=vertices_inputs
            ))
        self.scene.add_geometry(geometry)

        return geometry
