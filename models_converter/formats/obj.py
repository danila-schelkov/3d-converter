def _(*args):
    print('[ScwUtils]', end=' ')
    for arg in args:
        print(arg, end=' ')
    print()


class Writer:
    def __init__(self):
        self.writen = ''

        self.temp_vertices_offsets = {
            'POSITION': 0,
            'TEXCOORD': 0,
            'NORMAL': 0
        }

        self.vertices_offsets = {
            'POSITION': 0,
            'TEXCOORD': 0,
            'NORMAL': 0
        }

    def write(self, data: dict):
        for geom in data['geometries']:
            for key in self.vertices_offsets.keys():
                self.vertices_offsets[key] = self.temp_vertices_offsets[key]
            prefix = ''

            name = geom['name']
            vertices = geom['vertices']
            materials = geom['materials']
            for vertex in vertices:
                if vertex['type'] == 'POSITION':
                    prefix = 'v '
                elif vertex['type'] == 'NORMAL':
                    prefix = 'vn '
                elif vertex['type'] == 'TEXCOORD':
                    prefix = 'vt '

                self.temp_vertices_offsets[vertex['type']] += len(vertex['vertex'])

                for item in vertex['vertex']:
                    temp_string = prefix
                    for subitem in item:
                        temp_string += str(subitem * vertex['scale']) + ' '
                    self.writen += f'{temp_string}\n'
                self.writen += '\n\n'
            for material in materials:
                self.writen += f'o {name}|{material["name"]}\n\n'
                for item in material['polygons']:
                    temp_string = 'f '
                    for subitem in item:
                        temp_list = [
                            str(subitem[0] + self.vertices_offsets['POSITION'] + 1),  # POSITION
                            str(subitem[2] + self.vertices_offsets['TEXCOORD'] + 1),  # TEXCOORD
                            str(subitem[1] + self.vertices_offsets['NORMAL'] + 1)  # NORMAL
                        ]

                        temp_string += '/'.join(temp_list) + ' '
                    self.writen += f'{temp_string}\n'
                self.writen += '\n\n'


class Parser:
    def __init__(self, file_data: bytes or str):
        if type(file_data) is bytes:
            file_data = file_data.decode()

        self.parsed = {'header': {'version': 2,
                                  'frame_rate': 30,
                                  'first_frame': 0,
                                  'last_frame': 0,
                                  'materials_file': 'sc3d/character_materials.scw'},
                       'materials': [],
                       'geometries': [],
                       'cameras': [],
                       'nodes': []}

        self.lines = file_data.split('\n')

        self.position_temp, self.position = [], []
        self.normals_temp, self.normals = [], []
        self.texcoord_temp, self.texcoord = [], []

    def parse(self):
        polygons = []
        geometry_name = None
        material = 'character_mat'
        position_scale, normals_scale, texcoord_scale = 1, 1, 1

        vertices_offsets = {
            'POSITION': 0,
            'TEXCOORD': 0,
            'NORMAL': 0
        }

        names = [line[2:].split('|')[0]
                 for line in list(filter(lambda line: line.startswith('o '), self.lines))]

        for line_index in range(len(self.lines)):
            line = self.lines[line_index]
            items = line.split()[1:]
            if line.startswith('v '):  # POSITION
                for item in items:
                    self.position_temp.append(float(item))
            elif line.startswith('vn '):  # NORMAL
                for item in items:
                    self.normals_temp.append(float(item))
            elif line.startswith('vt '):  # TEXCOORD
                if len(items) > 2:
                    items = items[:-1]
                for item in items:
                    self.texcoord_temp.append(float(item))
            elif line.startswith('f '):
                temp_list = []
                if len(items) > 3:
                    _('It is necessary to triangulate the model')
                    break
                for item in items:
                    second_temp_list = []
                    if len(item.split('/')) == 2:
                        _('Model have not normals or texture')
                        break
                    elif len(item.split('/')) == 1:
                        _('Model have not normals and texture')
                        break
                    for x in item.split('/'):
                        second_temp_list.append(int(x) - 1)
                    temp_list.append([second_temp_list[0] - vertices_offsets['POSITION'],
                                      second_temp_list[2] - vertices_offsets['TEXCOORD'],
                                      second_temp_list[1] - vertices_offsets['NORMAL']])
                polygons.append(temp_list)
            elif line.startswith('o '):
                geometry_name = items[0]
                if '|' in items[0]:
                    geometry_name, material = items[0].split('|')

                if self.position_temp:
                    self.position = []
                    position_scale = self.get_vertex_scale(self.position_temp)
                    for x in range(0, len(self.position_temp), 3):
                        self.position.append([vertex / position_scale for vertex in self.position_temp[x: x + 3]])

                if self.normals_temp:
                    self.normals = []
                    normals_scale = self.get_vertex_scale(self.normals_temp)
                    for x in range(0, len(self.normals_temp), 3):
                        self.normals.append([vertex / normals_scale for vertex in self.normals_temp[x: x + 3]])

                if self.texcoord_temp:
                    self.texcoord = []
                    texcoord_scale = self.get_vertex_scale(self.texcoord_temp)
                    for x in range(0, len(self.texcoord_temp), 2):
                        self.texcoord.append([vertex / texcoord_scale for vertex in self.texcoord_temp[x: x + 2]])

            if not line.startswith('f ') and polygons and geometry_name and \
                    self.position and self.normals and self.texcoord:
                self.position_temp = []
                self.normals_temp = []
                self.texcoord_temp = []

                if len(names) >= len(self.parsed['geometries']) + 1 and \
                        names[len(self.parsed['geometries']) + 1] != geometry_name:
                    vertices_offsets['POSITION'] += len(self.position)
                    vertices_offsets['TEXCOORD'] += len(self.normals)
                    vertices_offsets['NORMAL'] += len(self.texcoord)
                if not (self.parsed['geometries'] and self.parsed['geometries'][-1]['name'] == geometry_name):
                    self.parsed['geometries'].append({
                        'name': geometry_name,
                        'group': '',
                        'vertices': [
                            {
                                'type': 'POSITION',
                                'name': 'position_0',
                                'index': 0,
                                'scale': position_scale,
                                'vertex': self.position
                            },
                            {
                                'type': 'NORMAL',
                                'name': 'normal_0',
                                'index': 1,
                                'scale': normals_scale,
                                'vertex': self.normals
                            },
                            {
                                'type': 'TEXCOORD',
                                'name': 'texcoord_0',
                                'index': 2,
                                'scale': texcoord_scale,
                                'vertex': self.texcoord
                            }
                        ],
                        'have_bind_matrix': False,
                        'materials': []
                    })
                self.parsed['geometries'][-1]['materials'].append(
                    {'name': material, 'polygons': polygons, 'inputs': [
                        {'offset': self.parsed['geometries'][-1]['vertices'].index(vertex),
                         'name': vertex['name'],
                         'type': vertex['type']}
                        for vertex in self.parsed['geometries'][-1]['vertices']
                    ]}
                )

                material = 'character_mat'
                polygons = []

        for geometry in self.parsed['geometries']:
            self.parsed['nodes'].append({
                'name': geometry['name'],
                'parent': '',
                'instances': [
                    {
                        'instance_name': geometry['name'],
                        'instance_type': 'GEOM',
                        'binds': [
                            {'symbol': material['name'], 'target': material['name']}
                            for material in geometry['materials']
                        ]
                    }
                ],
                'frames': [
                    {
                        'frame_id': 0,
                        'rotation': {'x': 0, 'y': 0, 'z': 0, 'w': 0},
                        'position': {'x': 0, 'y': 0, 'z': 0},
                        'scale': {'x': 1, 'y': 1, 'z': 1}
                    }
                ],
                'frames_settings': [False] * 8
            })

    @staticmethod
    def get_vertex_scale(vertex_data: list):
        vertex_scale = max(max(vertex_data), abs(min(vertex_data)))
        if vertex_scale < 1:
            vertex_scale = 1
        return vertex_scale
