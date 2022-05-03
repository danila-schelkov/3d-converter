from models_converter.formats.universal import Scene, Node, Geometry
from models_converter.interfaces import ParserInterface
from models_converter.utilities.math import Vector3, Quaternion


class Parser(ParserInterface):
    def __init__(self, file_data: bytes or str):
        if type(file_data) is bytes:
            file_data = file_data.decode()

        self.scene = Scene()

        self.lines = file_data.split('\n')

        self.position_temp, self.position = [], []
        self.normals_temp, self.normals = [], []
        self.texcoord_temp, self.texcoord = [], []

    def parse(self):
        triangles = []
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
                    raise ValueError('It is necessary to triangulate the model')
                for item in items:
                    second_temp_list = []
                    if len(item.split('/')) == 2:
                        raise ValueError('Model have not normals or texture')
                    elif len(item.split('/')) == 1:
                        raise ValueError('Model have not normals and texture')
                    for x in item.split('/'):
                        second_temp_list.append(int(x) - 1)
                    temp_list.append([second_temp_list[0] - vertices_offsets['POSITION'],
                                      second_temp_list[2] - vertices_offsets['TEXCOORD'],
                                      second_temp_list[1] - vertices_offsets['NORMAL']])
                triangles.append(temp_list)
            elif line.startswith('o '):
                geometry_name = items[0]
                if '|' in items[0]:
                    geometry_name, material = items[0].split('|')

                if self.position_temp:
                    self.position = []
                    position_scale = self._get_vertex_scale(self.position_temp)
                    for x in range(0, len(self.position_temp), 3):
                        self.position.append([vertex / position_scale for vertex in self.position_temp[x: x + 3]])

                if self.normals_temp:
                    self.normals = []
                    normals_scale = self._get_vertex_scale(self.normals_temp)
                    for x in range(0, len(self.normals_temp), 3):
                        self.normals.append([vertex / normals_scale for vertex in self.normals_temp[x: x + 3]])

                if self.texcoord_temp:
                    self.texcoord = []
                    texcoord_scale = self._get_vertex_scale(self.texcoord_temp)
                    for x in range(0, len(self.texcoord_temp), 2):
                        self.texcoord.append([vertex / texcoord_scale for vertex in self.texcoord_temp[x: x + 2]])

            if not line.startswith('f ') and triangles and geometry_name and \
                    self.position and self.normals and self.texcoord:
                self.position_temp = []
                self.normals_temp = []
                self.texcoord_temp = []

                if len(names) > len(self.scene.get_geometries()) + 1 and \
                        names[len(self.scene.get_geometries()) + 1] != geometry_name:
                    vertices_offsets['POSITION'] += len(self.position)
                    vertices_offsets['TEXCOORD'] += len(self.normals)
                    vertices_offsets['NORMAL'] += len(self.texcoord)
                if not (self.scene.get_geometries() and self.scene.get_geometries()[-1].get_name() == geometry_name):
                    geometry = Geometry(name=geometry_name, group='GEO')
                    geometry.add_vertex(Geometry.Vertex(
                        name='position_0',
                        vertex_type='POSITION',
                        vertex_index=0,
                        vertex_scale=position_scale,
                        points=self.position
                    ))
                    geometry.add_vertex(Geometry.Vertex(
                        name='normal_0',
                        vertex_type='NORMAL',
                        vertex_index=1,
                        vertex_scale=normals_scale,
                        points=self.normals
                    ))
                    geometry.add_vertex(Geometry.Vertex(
                        name='texcoord_0',
                        vertex_type='TEXCOORD',
                        vertex_index=2,
                        vertex_scale=texcoord_scale,
                        points=self.texcoord
                    ))
                    self.scene.add_geometry(geometry)
                self.scene.get_geometries()[-1].add_material(
                    Geometry.Material(material, triangles)
                )

                material = 'character_mat'
                triangles = []

        for geometry in self.scene.get_geometries():
            node = Node(name=geometry.get_name(), parent='')
            instance = Node.Instance(name=geometry.get_name(), instance_type='GEOM')
            for material in geometry.get_materials():
                instance.add_bind(material.get_name(), material.get_name())
            node.add_instance(instance)

            node.add_frame(Node.Frame(0, Vector3(), Vector3(1, 1, 1), Quaternion()))

            self.scene.add_node(node)

    @staticmethod
    def _get_vertex_scale(vertex_data: list):
        vertex_scale = max(max(vertex_data), abs(min(vertex_data)))
        if vertex_scale < 1:
            vertex_scale = 1
        return vertex_scale
