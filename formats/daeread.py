from xml.etree.ElementTree import *


def _(*args):
    print('[ScwUtils]', end=' ')
    for arg in args:
        print(arg, end=' ')
    print()


class Reader:
    def node(self, nodes):
        namespaces = {
            'collada': 'http://www.collada.org/2005/11/COLLADASchema'
        }

        nodes_list = []
        for node in nodes:
            instance_geometry = node.findall('collada:instance_geometry', namespaces)
            instance_controller = node.findall('collada:instance_controller', namespaces)

            childrens = self.node(node.findall('collada:node', namespaces))
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
                    geometry_url = instance_geometry[0].attrib['url'][1:]
                    node_data['target'] = geometry_url
                elif instance_controller:
                    controller_url = instance_controller[0].attrib['url'][1:]
                    node_data['target'] = controller_url

                node_data['binds'] = binds

            node_data['childrens'] = childrens

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

            # node_data['frames'] = node['frames']
            self.fixed_nodes_list.append(node_data)

            for children in node['childrens']:
                children_data = {
                    'name': children['name'],
                    'parent': node['name'],
                    'has_target': children['has_target']
                }

                if children_data['has_target']:
                    children_data['target_type'] = children['target_type']
                    children_data['target'] = children['target']
                    children_data['binds'] = children['binds']

                # children_data['frames'] = children['frames']
                self.fixed_nodes_list.append(children_data)
                self.fix_nodes_list(children['childrens'], node_data['name'])

    def __init__(self, file_data):
        self.fixed_nodes_list = []
        root = fromstring(file_data)
        # tree = parse(file_path)
        # root = tree.getroot()

        namespaces = {
            'collada': 'http://www.collada.org/2005/11/COLLADASchema'
        }

        # Libraries
        self.library_geometries = root.find('./collada:library_geometries', namespaces)
        self.library_controllers = root.find('./collada:library_controllers', namespaces)
        library_scenes = root.find('./collada:library_visual_scenes', namespaces)
        # Libraries

        instance_scene = root.find('./collada:scene', namespaces).find('collada:instance_visual_scene', namespaces)
        scene_url = instance_scene.attrib['url'][1:]
        scene = library_scenes.find(f'collada:visual_scene[@id="{scene_url}"]', namespaces)

        nodes = self.node(scene.findall('collada:node', namespaces))
        self.fix_nodes_list(nodes)

        for node in self.fixed_nodes_list:
            if node['has_target']:
                controller = None
                geometry = None

                if node['target_type'] == 'CONT':
                    controller = self.library_controllers \
                        .find(f'collada:controller[@id="{node["target"]}"]', namespaces)

                    geometry_url = controller[0].attrib['source'][1:]
                    geometry = self.library_geometries \
                        .find(f'collada:geometry[@id="{geometry_url}"]', namespaces)
                elif node['target_type'] == 'GEOM':
                    geometry = self.library_geometries \
                        .find(f'collada:geometry[@id="{node["target"]}"]', namespaces)

                if geometry is not None:
                    name = geometry.attrib['id']
                    geometry_info = {'name': name,
                                     'group': node['parent'],
                                     'vertices': [],
                                     'have_bind_matrix': True if controller is not None else False,
                                     'materials': []}

                    mesh = geometry[0]
                    triangles = mesh.findall('collada:triangles', namespaces)
                    inputs = triangles[0].findall('collada:input', namespaces)
                    for _input in inputs:
                        semantic = _input.attrib['semantic']
                        source_link = _input.attrib['source'][1:]
                        source = mesh.find(f'*[@id="{source_link}"]')

                        if semantic == 'VERTEX':
                            vertices_input = source[0]
                            semantic = vertices_input.attrib['semantic']
                            source_link = vertices_input.attrib['source'][1:]
                            source = mesh.find(f'*[@id="{source_link}"]')

                        float_array = source.find('collada:float_array', namespaces)
                        accessor = source.find('collada:technique_common/collada:accessor', namespaces)

                        vertex_temp = [float(floating) for floating in float_array.text.split()]

                        scale = max(max(vertex_temp), abs(min(vertex_temp)))
                        if scale < 1:
                            scale = 1
                        if semantic == 'TEXCOORD':
                            vertex_temp[1::2] = [1 - x for x in vertex_temp[1::2]]

                        vertex = []
                        for x in range(0, len(vertex_temp) // len(accessor), len(accessor)):
                            vertex.append(vertex_temp[x: x + len(accessor)])

                        geometry_info['vertices'].append({'type': semantic,
                                                          'index': 0,
                                                          'scale': scale,
                                                          'vertex': vertex})
                    for triangle in triangles:
                        triangles_material = triangle.attrib['material']

                        p = triangle.find('collada:p', namespaces)
                        polygons_temp = [int(integer) for integer in p.text.split()]

                        polygons = []
                        for x in range(0, len(polygons_temp) // len(inputs) // 3, len(inputs) * 3):
                            temp_list = []
                            for x1 in range(len(inputs)):
                                second_temp_list = []
                                for x2 in range(3):
                                    second_temp_list.append(polygons_temp[x + x1 + x2])
                                temp_list.append(second_temp_list)
                            polygons.append(temp_list)
                        geometry_info['materials'].append({'name': triangles_material,
                                                           'polygons': polygons})
                    print(geometry_info)

        #
        # technique_common = instance_geometry[0].find('.//collada:technique_common', namespaces)
        # instance_materials = technique_common.findall('collada:instance_material', namespaces)
        # for instance_material in instance_materials:
        #     symbol = instance_material.attrib['symbol']
        #     target = instance_material.attrib['target'][1:]
        #     print(symbol, target)

        # for material in root.findall('./collada:library_materials/collada:material', namespaces):
        #     name = material.attrib['id']
        #
        # geom_list = []
        # for geometry in root.findall('./collada:library_geometries/collada:geometry', namespaces):
        #     name = geometry.attrib['id']
        #     print(geometry.attrib)
        #     geom_dict = {'name': name,
        #                  'group': '',
        #                  'vertices': [],
        #                  'have_bind_matrix': False,
        #                  'materials': []}
        #
        #     mesh = geometry[0]
        #     triangles = mesh.findall('collada:triangles', namespaces)
        #     inputs = triangles[0].findall('collada:input', namespaces)
        #     for _input in inputs:
        #         semantic = _input.attrib['semantic']
        #         source_link = _input.attrib['source'][1:]
        #         source = mesh.find(f'*[@id="{source_link}"]')
        #
        #         if semantic == 'VERTEX':
        #             vertices_input = source[0]
        #             semantic = vertices_input.attrib['semantic']
        #             source_link = vertices_input.attrib['source'][1:]
        #             source = mesh.find(f'*[@id="{source_link}"]')
        #
        #         float_array = source.find('collada:float_array', namespaces)
        #         accessor = source.find('collada:technique_common/collada:accessor', namespaces)
        #
        #         vertex_temp = [float(floating) for floating in float_array.text.split()]
        #
        #         scale = max(max(vertex_temp), abs(min(vertex_temp)))
        #         if semantic == 'TEXCOORD':
        #             vertex_temp[1::2] = [1 - x for x in vertex_temp[1::2]]
        #
        #         vertex = []
        #         for x in range(0, len(vertex_temp) // len(accessor), len(accessor)):
        #             vertex.append(vertex_temp[x: x + len(accessor)])
        #
        #         geom_dict['vertices'].append({'type': semantic,
        #                                       'index': 0,
        #                                       'scale': scale,
        #                                       'vertex': vertex})
        #     for triangle in triangles:
        #         triangles_material = triangle.attrib['material']
        #
        #         p = triangle.find('collada:p', namespaces)
        #         polygons_temp = [int(integer) for integer in p.text.split()]
        #
        #         polygons = []
        #         for x in range(0, len(polygons_temp) // len(inputs) // 3, len(inputs) * 3):
        #             temp_list = []
        #             for x1 in range(len(inputs)):
        #                 second_temp_list = []
        #                 for x2 in range(3):
        #                     second_temp_list.append(polygons_temp[x + x1 + x2])
        #                 temp_list.append(second_temp_list)
        #             polygons.append(temp_list)
        #         geom_dict['materials'].append({'name': triangles_material,
        #                                        'polygons': polygons})
        #     geom_list.append(geom_dict)


if __name__ == '__main__':
    reader = Reader(open('../8bit_geo.dae').read())
