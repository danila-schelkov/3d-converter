def _(*args):
    print('[ScwUtils]', end=' ')
    for arg in args:
        print(arg, end=' ')
    print()


class Parser:
    def __init__(self, file_data: str):
        # <Variables>

        # <Vertices>
        vertex_temp, vertex = [], []
        normals_temp, normals = [], []
        texcoord_temp, texcoord = [], []
        # </Vertices>

        polygons = []

        # </Variables>

        for line in file_data.split('\n'):
            items = line.split()[1:]
            if line.startswith('v '):  # POSITION
                temp_list = []
                for item in items:
                    vertex_temp.append(float(item))
                    temp_list.append(float(item))
                vertex.append(temp_list)
            elif line.startswith('vn '):  # NORMAL
                temp_list = []
                for item in items:
                    normals_temp.append(float(item))
                    temp_list.append(float(item))
                normals.append(temp_list)
            elif line.startswith('vt '):  # TEXCOORD
                if len(items) > 2:
                    items = items[:-1]
                temp_list = []
                for item in items:
                    texcoord_temp.append(float(item))
                    temp_list.append(float(item))
                texcoord.append(temp_list)
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
                        second_temp_list.append(int(x)-1)
                    temp_list.append([second_temp_list[0], second_temp_list[2], second_temp_list[1]])
                polygons.append(temp_list)
        vertex_scale = max(max(vertex_temp), abs(min(vertex_temp)))
        if vertex_scale < 1:
            vertex_scale = 1
        normals_scale = max(max(normals_temp), abs(min(normals_temp)))
        if normals_scale < 1:
            normals_scale = 1
        texcoord_scale = max(max(texcoord_temp), abs(min(texcoord_temp)))
        if texcoord_scale < 1:
            texcoord_scale = 1
        self.parsed = {'name': '',
                       'group': '',
                       'vertices': [{'type': 'POSITION', 'index': 0, 'scale': vertex_scale, 'vertex': vertex},
                                    {'type': 'NORMAL', 'index': 1, 'scale': normals_scale, 'vertex': normals},
                                    {'type': 'TEXCOORD', 'index': 2, 'scale': texcoord_scale, 'vertex': texcoord}],
                       'have_bind_matrix': False,
                       'materials': [{'name': 'character_mat', 'polygons': polygons}]}
