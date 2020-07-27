def _(*args):
    print('[ScwUtils]', end=' ')
    for arg in args:
        print(arg, end=' ')
    print()


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
        geometry_name = 'This model haven\'t a name!:( Its VERY SAD!'
        is_first_name = True
        for line in self.lines:
            items = line.split()[1:]
            if line.startswith('v '):  # POSITION
                temp_list = []
                for item in items:
                    self.position_temp.append(float(item))
                    temp_list.append(float(item))
                self.position.append(temp_list)
            elif line.startswith('vn '):  # NORMAL
                temp_list = []
                for item in items:
                    self.normals_temp.append(float(item))
                    temp_list.append(float(item))
                self.normals.append(temp_list)
            elif line.startswith('vt '):  # TEXCOORD
                if len(items) > 2:
                    items = items[:-1]
                temp_list = []
                for item in items:
                    self.texcoord_temp.append(float(item))
                    temp_list.append(float(item))
                self.texcoord.append(temp_list)
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
                #         'name': geometry_name,
                #         'group': '',
                #         'vertices': [
                #             {'type': 'POSITION', 'index': 0, 'scale': position_scale, 'vertex': self.position},
                #             {'type': 'NORMAL', 'index': 1, 'scale': normals_scale, 'vertex': self.normals},
                #             {'type': 'TEXCOORD', 'index': 2, 'scale': texcoord_scale, 'vertex': self.texcoord}
                #         ],
                #         'have_bind_matrix': False,
                #         'materials': [{'name': 'character_mat', 'polygons': self.polygons}]
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

        self.parsed['geometries'].append({
            'name': geometry_name,
            'group': '',
            'vertices': [
                {'type': 'POSITION', 'index': 0, 'scale': position_scale, 'vertex': self.position},
                {'type': 'NORMAL', 'index': 1, 'scale': normals_scale, 'vertex': self.normals},
                {'type': 'TEXCOORD', 'index': 2, 'scale': texcoord_scale, 'vertex': self.texcoord}
            ],
            'have_bind_matrix': False,
            'materials': [{'name': 'character_mat', 'polygons': self.polygons}]
        })

    @staticmethod
    def get_vertex_scale(vertex_data: list):
        vertex_scale = max(max(vertex_data), abs(min(vertex_data)))
        if vertex_scale < 1:
            vertex_scale = 1
        return vertex_scale
