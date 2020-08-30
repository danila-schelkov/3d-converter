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
