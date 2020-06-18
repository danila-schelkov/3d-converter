def _(*args):
    print('[ScwUtils]', end=' ')
    for arg in args:
        print(arg, end=' ')
    print()


class Writer:
    def __init__(self, info: list):
        self.writen = ''
        for geom in info:
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
                        temp_list = []
                        for subitem_of_subitem in [subitem[0], subitem[2], subitem[1]]:
                            temp_list.append(str(subitem_of_subitem + 1))
                        temp_string += '/'.join(temp_list) + ' '
                    self.writen += f'{temp_string}\n'
                self.writen += '\n\n'
