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
                self.writen += f'o {name}_{material["name"]}\n\n'
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
    def __init__(self, file_data: str):
        # <Variables>

        self.parsed = {'header': {'version': 2,
                                  'frame_rate': 30,
                                  'materials_file': 'sc3d/character_materials.scw'},
                       'materials': [],
                       'geometries': [],
                       'cameras': [],
                       'nodes': []}

        self.lines = file_data.split('\n')

        # <Vertices>
        self.position_temp, self.position = [], []
        self.normals_temp, self.normals = [], []
        self.texcoord_temp, self.texcoord = [], []
        # </Vertices>

        self.polygons = []

        # </Variables>

        self.parse()

    def parse(self):
        geometry_name = 'This model haven \'t a chunk_name!:( Its VERY SAD!'
        is_first_name = True
        for line in self.lines:
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
                    temp_list.append([second_temp_list[0], second_temp_list[2], second_temp_list[1]])
                self.polygons.append(temp_list)
            elif line.startswith('o '):
                # if not is_first_name:
                #     position_scale = self.get_vertex_scale(self.position_temp)
                #     normals_scale = self.get_vertex_scale(self.normals_temp)
                #     texcoord_scale = self.get_vertex_scale(self.texcoord_temp)
                #
                #     self.parsed['geometries'].append({
                #         'chunk_name': geometry_name,
                #         'group': '',
                #         'vertices': [
                #             {'type': 'POSITION', 'index': 0, 'scale': position_scale, 'vertex': self.position},
                #             {'type': 'NORMAL', 'index': 1, 'scale': normals_scale, 'vertex': self.normals},
                #             {'type': 'TEXCOORD', 'index': 2, 'scale': texcoord_scale, 'vertex': self.texcoord}
                #         ],
                #         'have_bind_matrix': False,
                #         'materials': [{'chunk_name': 'character_mat', 'polygons': self.polygons}]
                #     })
                #
                #     # <VariablesReset>
                #
                #     # <Vertices>
                #     self.position_temp, self.position = [], []
                #     self.normals_temp, self.normals = [], []
                #     self.texcoord_temp, self.texcoord = [], []
                #     # </Vertices>
                #
                #     self.polygons = []
                #
                #     # </VariablesReset>
                # geometry_name = line.split('o ')[0]
                if is_first_name:
                    geometry_name = line.split('o ')[0]

        position_scale = self.get_vertex_scale(self.position_temp)
        normals_scale = self.get_vertex_scale(self.normals_temp)
        texcoord_scale = self.get_vertex_scale(self.texcoord_temp)

        for x in range(0, len(self.position_temp), 3):
            self.position.append(self.position_temp[x: x + 3])

        for x in range(0, len(self.normals_temp), 3):
            self.normals.append(self.normals_temp[x: x + 3])

        for x in range(0, len(self.texcoord_temp), 2):
            self.texcoord.append(self.texcoord_temp[x: x + 2])

        self.parsed['geometries'].append({
            'chunk_name': geometry_name,
            'group': '',
            'vertices': [
                {'type': 'POSITION', 'index': 0, 'scale': position_scale, 'vertex': self.position},
                {'type': 'NORMAL', 'index': 1, 'scale': normals_scale, 'vertex': self.normals},
                {'type': 'TEXCOORD', 'index': 2, 'scale': texcoord_scale, 'vertex': self.texcoord}
            ],
            'have_bind_matrix': False,
            'materials': [{'chunk_name': 'character_mat', 'polygons': self.polygons}]
        })

        # TODO: nodes

    @staticmethod
    def get_vertex_scale(vertex_data: list):
        vertex_scale = max(max(vertex_data), abs(min(vertex_data)))
        if vertex_scale < 1:
            vertex_scale = 1
        return vertex_scale
