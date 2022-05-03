from models_converter.formats.universal import Scene
from models_converter.interfaces import WriterInterface


class Writer(WriterInterface):
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

    def write(self, scene: Scene):
        for geometry in scene.get_geometries():
            for key in self.vertices_offsets.keys():
                self.vertices_offsets[key] = self.temp_vertices_offsets[key]
            prefix = ''

            for vertex in geometry.get_vertices():
                if vertex.get_type() == 'POSITION':
                    prefix = 'v '
                elif vertex.get_type() == 'NORMAL':
                    prefix = 'vn '
                elif vertex.get_type() == 'TEXCOORD':
                    prefix = 'vt '

                self.temp_vertices_offsets[vertex.get_type()] += len(vertex.get_points())

                for triangle in vertex.get_points():
                    temp_string = prefix
                    for point in triangle:
                        temp_string += str(point * vertex.get_scale()) + ' '
                    self.writen += f'{temp_string}\n'
                self.writen += '\n\n'
            for material in geometry.get_materials():
                self.writen += f'o {geometry.get_name()}|{material.get_name()}\n\n'
                for triangle in material.get_triangles():
                    temp_string = 'f '
                    for point in triangle:
                        temp_list = [
                            str(point[0] + self.vertices_offsets['POSITION'] + 1),  # POSITION
                            str(point[2] + self.vertices_offsets['TEXCOORD'] + 1),  # TEXCOORD
                            str(point[1] + self.vertices_offsets['NORMAL'] + 1)  # NORMAL
                        ]

                        temp_string += '/'.join(temp_list) + ' '
                    self.writen += f'{temp_string}\n'
                self.writen += '\n\n'
