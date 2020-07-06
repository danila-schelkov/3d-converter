from xml.etree.ElementTree import *

from formats.scwwrite import Writer


def _(*args):
    print('[ScwUtils]', end=' ')
    for arg in args:
        print(arg, end=' ')
    print()


class Parser:
    def node(self, nodes):
        namespaces = {
            'collada': 'http://www.collada.org/2005/11/COLLADASchema'
        }

        nodes_list = []
        for node in nodes:
            instance_geometry = node.findall('collada:instance_geometry', namespaces)
            instance_controller = node.findall('collada:instance_controller', namespaces)

            children = self.node(node.findall('collada:node', namespaces))
            node_data = {
                'name': node.attrib['id'],
                'has_target': True if instance_geometry or instance_controller else False
            }

            if node_data['has_target']:
                binds = []

                if instance_geometry:
                    for instance_material in instance_geometry[0][0][0]:
                        binds.append({
                            'symbol': instance_material.attrib['symbol'],
                            'target': instance_material.attrib['target'][1:]
                        })
                elif instance_controller:
                    for instance_material in instance_controller[0][0][0]:
                        binds.append({
                            'symbol': instance_material.attrib['symbol'],
                            'target': instance_material.attrib['target'][1:]
                        })

                if instance_geometry:
                    node_data['target_type'] = 'GEOM'
                elif instance_controller:
                    node_data['target_type'] = 'CONT'

                if instance_geometry:
                    geometry_url = instance_geometry[0].attrib['url']
                    node_data['target'] = geometry_url[1:]
                elif instance_controller:
                    controller_url = instance_controller[0].attrib['url']
                    node_data['target'] = controller_url[1:]

                node_data['binds'] = binds

            node_data['children'] = children

            nodes_list.append(node_data)

        return nodes_list

    def fix_nodes_list(self, nodes, parent: str = ''):
        for node in nodes:
            node_data = {
                'name': node['name'],
                'parent': parent,
                'has_target': node['has_target']
            }

            if node_data['has_target']:
                node_data['target_type'] = node['target_type']
                node_data['target'] = node['target']
                node_data['binds'] = node['binds']

            if not node_data['has_target']:
                node_data['frames_settings'] = [0, 0, 0, 0, 0, 0, 0, 0]
                node_data['frames'] = [{
                    'frame_id': 0,
                    'rotation': {'x': 0, 'y': 0, 'z': 0, 'w': 0},
                    'position': {'x': 0, 'y': 0, 'z': 0},
                    'scale': {'x': 1, 'y': 1, 'z': 1}
                }]
            else:
                node_data['frames'] = []

            # node_data['frames'] = node['frames']
            self.file_data['nodes'].append(node_data)
            self.fix_nodes_list(node['children'], node['name'])

    def __init__(self, file_data):
        self.file_data = {'header': {'version': 2,
                                     'materials_file': 'sc3d/character_materials.scw'},
                          'materials': [],
                          'geometries': [],
                          'cameras': [],
                          'nodes': []}

        self.geometry_info = {}

        root = fromstring(file_data)
        # tree = parse(file_path)
        # root = tree.getroot()

        self.namespaces = {
            'collada': 'http://www.collada.org/2005/11/COLLADASchema'
        }

        # Libraries
        self.library_materials = root.find('./collada:library_geometries', self.namespaces)
        self.library_geometries = root.find('./collada:library_geometries', self.namespaces)
        self.library_controllers = root.find('./collada:library_controllers', self.namespaces)
        library_scenes = root.find('./collada:library_visual_scenes', self.namespaces)
        # Libraries

        instance_scene = root.find('./collada:scene', self.namespaces).find('collada:instance_visual_scene',
                                                                            self.namespaces)
        scene_url = instance_scene.attrib['url'][1:]
        scene = library_scenes.find(f'collada:visual_scene[@id="{scene_url}"]', self.namespaces)

        nodes = self.node(scene.findall('collada:node', self.namespaces))
        self.fix_nodes_list(nodes)

    def parse_nodes(self):
        nodes = self.file_data['nodes']
        for node in nodes:
            node: dict = node  # this line for fix "Expected type"
            if node['has_target']:
                controller = None
                geometry = None

                if node['target_type'] == 'CONT':
                    controller = self.library_controllers \
                        .find(f'collada:controller[@id="{node["target"]}"]', self.namespaces)

                    geometry_url = controller[0].attrib['source'][1:]
                    geometry = self.library_geometries \
                        .find(f'collada:geometry[@id="{geometry_url}"]', self.namespaces)
                elif node['target_type'] == 'GEOM':
                    geometry = self.library_geometries \
                        .find(f'collada:geometry[@id="{node["target"]}"]', self.namespaces)

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
                    for x in range(int(accessor_source.attrib['count'])):
                        matrix = [float(x) for x in accessor_source.text.split()[x * 16:(x + 1) * 16]]
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
            self.geometry_info['weights']['vertex_weight'] = v

    def parse_geometry(self, geometry):
        name = geometry.attrib['id']

        self.geometry_info['name'] = name

        mesh = geometry[0]
        triangles = mesh.findall('collada:triangles', self.namespaces)
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
        self.file_data['geometries'].append(self.geometry_info)


# NODES TEMPLATE
# {'name': ...,
#  'parent': ...,
#  'has_target': False,
#  'frames': [{'frame_id': 0,
#              'rotation': {'x': ...,
#                           'y': ...,
#                           'z': ...,
#                           'w': ...},
#              'position': {'x': ...,
#                           'y': ...,
#                           'z': ...},
#              'scale': {'x': ...,
#                        'y': ...,
#                        'z': ...},
#              }]}


if __name__ == '__main__':
    parser = Parser(open('../8bit_geo.dae').read())
    parser.parse_nodes()

    writer = Writer(parser.file_data)
    open('../8bit_geo.scw', 'wb').write(writer.writen)
