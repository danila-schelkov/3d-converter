class Geometry:
    class Vertex:
        def __init__(
            self,
            *,
            name: str,
            vertex_type: str,
            vertex_index: int,
            vertex_scale: float,
            points: list[list[float]]
        ):
            self._name: str = name
            self._type: str = vertex_type
            self._index: int = vertex_index
            self._scale: float = vertex_scale
            self._points: list[list[float]] = points

        def get_name(self) -> str:
            return self._name

        def get_type(self) -> str:
            return self._type

        def get_index(self) -> int:
            return self._index

        def get_point_size(self) -> int:
            return len(self._points[0])

        def get_scale(self) -> float:
            return self._scale

        def get_points(self) -> list[list[float]]:
            return self._points

    class Primitive:
        def __init__(
            self,
            material_name: str,
            triangles: list[list[list[int]]],
            input_vertices: list,
        ):
            self._material_name: str = material_name
            self._triangles: list[list[list[int]]] = triangles
            self._input_vertices: list[Geometry.Vertex] = input_vertices

        def get_material_name(self) -> str:
            return self._material_name

        def get_triangles(self) -> list[list[list[int]]]:
            return self._triangles

        # TODO: integrate to all formats
        def get_input_vertices(self) -> list:
            return self._input_vertices

    class Joint:
        def __init__(self, name: str, matrix: list[float]):
            self._name: str = name
            self._matrix: list[float] = matrix

        def get_name(self) -> str:
            return self._name

        def get_matrix(self) -> list[float]:
            return self._matrix

        def set_matrix(self, matrix: list[float]):
            self._matrix = matrix

    class Weight:
        def __init__(self, joint_index: int, strength: float):
            self._joint_index: int = joint_index
            self._strength: float = strength

        def get_joint_index(self) -> int:
            return self._joint_index

        def get_strength(self) -> float:
            return self._strength

    def __init__(self, *, name: str, group: str | None = None):
        self._name: str = name
        self._group: str | None = group
        self._vertices: list[Geometry.Vertex] = []
        self._primitives: list[Geometry.Primitive] = []
        self._bind_matrix: list[float] | None = None
        self._joints: list[Geometry.Joint] = []
        self._weights: list[Geometry.Weight] = []

    def get_name(self) -> str:
        return self._name

    def get_group(self) -> str | None:
        return self._group

    def get_vertices(self) -> list[Vertex]:
        return self._vertices

    def add_vertex(self, vertex: Vertex):
        self._vertices.append(vertex)

    def get_primitives(self) -> list[Primitive]:
        return self._primitives

    def add_primitive(self, primitive: Primitive):
        self._primitives.append(primitive)

    def has_controller(self) -> bool:
        return self._bind_matrix is not None

    def get_bind_matrix(self) -> list[float] | None:
        return self._bind_matrix

    def set_controller_bind_matrix(self, matrix: list[float] | None):
        self._bind_matrix = matrix

    def get_joints(self) -> list[Joint]:
        return self._joints

    def add_joint(self, joint: Joint):
        self._joints.append(joint)

    def get_weights(self) -> list[Weight]:
        return self._weights

    def add_weight(self, weight: Weight):
        self._weights.append(weight)
