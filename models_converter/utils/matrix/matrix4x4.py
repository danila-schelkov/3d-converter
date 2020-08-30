from .matrix3x3 import Matrix3x3
from . import Matrix


class Matrix4x4(Matrix):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.translation_matrix = None
        self.rotation_matrix = None
        self.scale_matrix = None

    def determinant(self):
        value1_1 = self.matrix[0][0]
        value1_2 = self.matrix[0][1]
        value1_3 = self.matrix[0][2]
        value1_4 = self.matrix[0][3]

        value2_1 = self.matrix[1][0]
        value2_2 = self.matrix[1][1]
        value2_3 = self.matrix[1][2]
        value2_4 = self.matrix[1][3]

        value3_1 = self.matrix[2][0]
        value3_2 = self.matrix[2][1]
        value3_3 = self.matrix[2][2]
        value3_4 = self.matrix[2][3]

        value4_1 = self.matrix[3][0]
        value4_2 = self.matrix[3][1]
        value4_3 = self.matrix[3][2]
        value4_4 = self.matrix[3][3]

        matrix1 = Matrix3x3(matrix=(
            (value2_2, value2_3, value2_4),
            (value3_2, value3_3, value3_4),
            (value4_2, value4_3, value4_4)
        ))

        matrix2 = Matrix3x3(matrix=(
            (value2_1, value2_3, value2_4),
            (value3_1, value3_3, value3_4),
            (value4_1, value4_3, value4_4)
        ))

        matrix3 = Matrix3x3(matrix=(
            (value2_1, value2_2, value2_4),
            (value3_1, value3_2, value3_4),
            (value4_1, value4_2, value4_4)
        ))

        matrix4 = Matrix3x3(matrix=(
            (value2_1, value2_2, value2_3),
            (value3_1, value3_2, value3_3),
            (value4_1, value4_2, value4_3)
        ))

        det = value1_1 * matrix1.determinant()
        det -= value1_2 * matrix2.determinant()
        det += value1_3 * matrix3.determinant()
        det -= value1_4 * matrix4.determinant()

        return det

    def cofactor(self):
        value1_1 = self.matrix[0][0]
        value1_2 = self.matrix[0][1]
        value1_3 = self.matrix[0][2]
        value1_4 = self.matrix[0][3]

        value2_1 = self.matrix[1][0]
        value2_2 = self.matrix[1][1]
        value2_3 = self.matrix[1][2]
        value2_4 = self.matrix[1][3]

        value3_1 = self.matrix[2][0]
        value3_2 = self.matrix[2][1]
        value3_3 = self.matrix[2][2]
        value3_4 = self.matrix[2][3]

        value4_1 = self.matrix[3][0]
        value4_2 = self.matrix[3][1]
        value4_3 = self.matrix[3][2]
        value4_4 = self.matrix[3][3]

        matrix1 = Matrix3x3(matrix=(
            (value2_2, value2_3, value2_4),
            (value3_2, value3_3, value3_4),
            (value4_2, value4_3, value4_4)
        ))

        matrix2 = Matrix3x3(matrix=(
            (value2_1, value2_3, value2_4),
            (value3_1, value3_3, value3_4),
            (value4_1, value4_3, value4_4)
        ))

        matrix3 = Matrix3x3(matrix=(
            (value2_1, value2_2, value2_4),
            (value3_1, value3_2, value3_4),
            (value4_1, value4_2, value4_4)
        ))

        matrix4 = Matrix3x3(matrix=(
            (value2_1, value2_2, value2_3),
            (value3_1, value3_2, value3_3),
            (value4_1, value4_2, value4_3)
        ))

        matrix5 = Matrix3x3(matrix=(
            (value1_2, value1_3, value1_4),
            (value3_2, value3_3, value3_4),
            (value4_2, value4_3, value4_4)
        ))

        matrix6 = Matrix3x3(matrix=(
            (value1_1, value1_3, value1_4),
            (value3_1, value3_3, value3_4),
            (value4_1, value4_3, value4_4)
        ))

        matrix7 = Matrix3x3(matrix=(
            (value1_1, value1_2, value1_4),
            (value3_1, value3_2, value3_4),
            (value4_1, value4_2, value4_4)
        ))

        matrix8 = Matrix3x3(matrix=(
            (value1_1, value1_2, value1_3),
            (value3_1, value3_2, value3_3),
            (value4_1, value4_2, value4_3)
        ))

        matrix9 = Matrix3x3(matrix=(
            (value1_2, value1_3, value1_4),
            (value2_2, value2_3, value2_4),
            (value4_2, value4_3, value4_4)
        ))

        matrix10 = Matrix3x3(matrix=(
            (value1_1, value1_3, value1_4),
            (value2_1, value2_3, value2_4),
            (value4_1, value4_3, value4_4)
        ))

        matrix11 = Matrix3x3(matrix=(
            (value1_1, value1_2, value1_4),
            (value2_1, value2_2, value2_4),
            (value4_1, value4_2, value4_4)
        ))

        matrix12 = Matrix3x3(matrix=(
            (value1_1, value1_2, value1_3),
            (value2_1, value2_2, value2_3),
            (value4_1, value4_2, value4_3)
        ))

        matrix13 = Matrix3x3(matrix=(
            (value1_2, value1_3, value1_4),
            (value2_2, value2_3, value2_4),
            (value3_2, value3_3, value3_4)
        ))

        matrix14 = Matrix3x3(matrix=(
            (value1_1, value1_3, value1_4),
            (value2_1, value2_3, value2_4),
            (value3_1, value3_3, value3_4)
        ))

        matrix15 = Matrix3x3(matrix=(
            (value1_1, value1_2, value1_4),
            (value2_1, value2_2, value2_4),
            (value3_1, value3_2, value3_4)
        ))

        matrix16 = Matrix3x3(matrix=(
            (value1_1, value1_2, value1_3),
            (value2_1, value2_2, value2_3),
            (value3_1, value3_2, value3_3)
        ))

        self.matrix = (
            (matrix1.determinant(), matrix2.determinant(), matrix3.determinant(), matrix4.determinant()),
            (matrix5.determinant(), matrix6.determinant(), matrix7.determinant(), matrix8.determinant()),
            (matrix9.determinant(), matrix10.determinant(), matrix11.determinant(), matrix12.determinant()),
            (matrix13.determinant(), matrix14.determinant(), matrix15.determinant(), matrix16.determinant())
        )

        self.find_cofactor()

    def put_rotation(self, xyz: tuple, w: float):
        x, y, z = xyz

        rotation_matrix = (
            (1-2*y**2-2*z**2, 2*x*y-2*z*w, 2*x*z+2*y*w, 0),  # x
            (2*x*y+2*z*w, 1-2*x**2-2*z**2, 2*y*z-2*x*w, 0),  # y
            (2*x*z-2*y*w, 2*y*z+2*x*w, 1-2*x**2-2*y**2, 0),  # z
            (0, 0, 0, 1)
        )

        self.rotation_matrix = Matrix4x4(matrix=rotation_matrix)

    def put_position(self, xyz: tuple):
        x, y, z = xyz

        translation_matrix = (
            (1, 0, 0, x),  # x
            (0, 1, 0, y),  # y
            (0, 0, 1, z),  # z
            (0, 0, 0, 1)
        )

        self.translation_matrix = Matrix4x4(matrix=translation_matrix)

    def put_scale(self, xyz: tuple):
        x, y, z = xyz

        scale_matrix = (
            (x, 0, 0, 0),
            (0, y, 0, 0),
            (0, 0, z, 0),
            (0, 0, 0, 1)
        )

        self.scale_matrix = Matrix4x4(matrix=scale_matrix)

    def get_rotation(self) -> dict:
        rotation = {
            'x': 0,
            'y': 0,
            'z': 0,
            'w': 0
        }

        return rotation

    def get_position(self) -> dict:
        position = (self.matrix[0][3], self.matrix[1][3], self.matrix[2][3])

        self.put_position(position)

        position = {
            'x': position[0],
            'y': position[1],
            'z': position[2]
        }

        return position

    def get_scale(self) -> dict:
        xyz = (1, 1, 1)

        self.put_scale(xyz)

        scale = {
            'x': xyz[0],
            'y': xyz[1],
            'z': xyz[2]
        }

        return scale
