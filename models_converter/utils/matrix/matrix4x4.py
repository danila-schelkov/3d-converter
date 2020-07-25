from .matrix3x3 import Matrix3x3


def matrix2tuple(matrix_list: list):
    new_matrix = [tuple(row) for row in matrix_list]
    new_matrix = tuple(new_matrix)

    return new_matrix


class Matrix4x4(object):
    def __init__(self, matrix_list: tuple = None):
        self.translation_matrix = None
        self.rotation_matrix = None
        self.scale_matrix = None

        if matrix_list is not None:
            self.matrix = matrix_list
        else:
            self.matrix = (
                (1, 0, 0, 0),  # x
                (0, 1, 0, 0),  # y
                (0, 0, 1, 0),  # z
                (0, 0, 0, 1)
            )

    def __matmul__(self, other):
        if len(self.matrix) != len(other.matrix[0]) or len(self.matrix[0]) != len(other.matrix):
            raise TypeError('Матрицы не могут быть перемножены')
        else:
            multiplied_matrix = []

            for row in self.matrix:
                matrix_row = []
                for column in range(4):
                    s = 0
                    for i in range(4):
                        s += row[i] * other.matrix[i][column]
                    matrix_row.append(s)
                multiplied_matrix.append(matrix_row)

            return Matrix4x4(matrix2tuple(multiplied_matrix))

    def __mul__(self, other: int or float):
        new_matrix = []
        for row in range(len(self.matrix)):
            new_row = []
            for column in range(len(self.matrix[0])):
                new_row.append(self.matrix[row][column]*other)
            new_matrix.append(new_row)

        return Matrix4x4(matrix2tuple(new_matrix))

    def __str__(self):
        return str(self.matrix)

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

        matrix1 = Matrix3x3((
            (value2_2, value2_3, value2_4),
            (value3_2, value3_3, value3_4),
            (value4_2, value4_3, value4_4)
        ))

        matrix2 = Matrix3x3((
            (value2_1, value2_3, value2_4),
            (value3_1, value3_3, value3_4),
            (value4_1, value4_3, value4_4)
        ))

        matrix3 = Matrix3x3((
            (value2_1, value2_2, value2_4),
            (value3_1, value3_2, value3_4),
            (value4_1, value4_2, value4_4)
        ))

        matrix4 = Matrix3x3((
            (value2_1, value2_2, value2_3),
            (value3_1, value3_2, value3_3),
            (value4_1, value4_2, value4_3)
        ))

        det = value1_1 * matrix1.determinant()
        det -= value1_2 * matrix2.determinant()
        det += value1_3 * matrix3.determinant()
        det -= value1_4 * matrix4.determinant()

        return det

    def transpose(self):
        height = len(self.matrix)
        width = len(self.matrix[0])

        self.matrix = [[self.matrix[row][col] for row in range(height)] for col in range(width)]
        self.matrix = [tuple(row) for row in self.matrix]
        self.matrix = tuple(self.matrix)

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

        matrix1 = Matrix3x3((
            (value2_2, value2_3, value2_4),
            (value3_2, value3_3, value3_4),
            (value4_2, value4_3, value4_4)
        ))

        matrix2 = Matrix3x3((
            (value2_1, value2_3, value2_4),
            (value3_1, value3_3, value3_4),
            (value4_1, value4_3, value4_4)
        ))

        matrix3 = Matrix3x3((
            (value2_1, value2_2, value2_4),
            (value3_1, value3_2, value3_4),
            (value4_1, value4_2, value4_4)
        ))

        matrix4 = Matrix3x3((
            (value2_1, value2_2, value2_3),
            (value3_1, value3_2, value3_3),
            (value4_1, value4_2, value4_3)
        ))

        matrix5 = Matrix3x3((
            (value1_2, value1_3, value1_4),
            (value3_2, value3_3, value3_4),
            (value4_2, value4_3, value4_4)
        ))

        matrix6 = Matrix3x3((
            (value1_1, value1_3, value1_4),
            (value3_1, value3_3, value3_4),
            (value4_1, value4_3, value4_4)
        ))

        matrix7 = Matrix3x3((
            (value1_1, value1_2, value1_4),
            (value3_1, value3_2, value3_4),
            (value4_1, value4_2, value4_4)
        ))

        matrix8 = Matrix3x3((
            (value1_1, value1_2, value1_3),
            (value3_1, value3_2, value3_3),
            (value4_1, value4_2, value4_3)
        ))

        matrix9 = Matrix3x3((
            (value1_2, value1_3, value1_4),
            (value2_2, value2_3, value2_4),
            (value4_2, value4_3, value4_4)
        ))

        matrix10 = Matrix3x3((
            (value1_1, value1_3, value1_4),
            (value2_1, value2_3, value2_4),
            (value4_1, value4_3, value4_4)
        ))

        matrix11 = Matrix3x3((
            (value1_1, value1_2, value1_4),
            (value2_1, value2_2, value2_4),
            (value4_1, value4_2, value4_4)
        ))

        matrix12 = Matrix3x3((
            (value1_1, value1_2, value1_3),
            (value2_1, value2_2, value2_3),
            (value4_1, value4_2, value4_3)
        ))

        matrix13 = Matrix3x3((
            (value1_2, value1_3, value1_4),
            (value2_2, value2_3, value2_4),
            (value3_2, value3_3, value3_4)
        ))

        matrix14 = Matrix3x3((
            (value1_1, value1_3, value1_4),
            (value2_1, value2_3, value2_4),
            (value3_1, value3_3, value3_4)
        ))

        matrix15 = Matrix3x3((
            (value1_1, value1_2, value1_4),
            (value2_1, value2_2, value2_4),
            (value3_1, value3_2, value3_4)
        ))

        matrix16 = Matrix3x3((
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

        cofactor_matrix = []
        for row in range(len(self.matrix)):
            new_row = []
            for column in range(len(self.matrix[0])):
                new_row.append(self.matrix[row][column] * (-1) ** (row + column))
            cofactor_matrix.append(new_row)
        self.matrix = cofactor_matrix

    def inverse(self):
        det = self.determinant()
        if det != 0:
            self.transpose()
            self.cofactor()

            self.matrix = self.__mul__(1 / det).matrix

        return self

    def put_rotation(self, xyz: tuple, w: float):
        x, y, z = xyz

        rotation_matrix = (
            (1-2*y**2-2*z**2, 2*x*y-2*z*w, 2*x*z+2*y*w, 0),  # x
            (2*x*y+2*z*w, 1-2*x**2-2*z**2, 2*y*z-2*x*w, 0),  # y
            (2*x*z-2*y*w, 2*y*z+2*x*w, 1-2*x**2-2*y**2, 0),  # z
            (0, 0, 0, 1)
        )

        self.rotation_matrix = Matrix4x4(rotation_matrix)

    def put_position(self, xyz: tuple):
        x, y, z = xyz

        translation_matrix = (
            (1, 0, 0, x),  # x
            (0, 1, 0, y),  # y
            (0, 0, 1, z),  # z
            (0, 0, 0, 1)
        )

        self.translation_matrix = Matrix4x4(translation_matrix)

    def put_scale(self, xyz: tuple):
        x, y, z = xyz

        scale_matrix = Matrix4x4((
            (x, 0, 0, 0),
            (0, y, 0, 0),
            (0, 0, z, 0),
            (0, 0, 0, 1)
        ))

        self.scale_matrix = scale_matrix

    def get_rotation(self):
        pass

    def get_position(self):
        xyz = (self.matrix[0][3], self.matrix[1][3], self.matrix[2][3])

        self.put_position(xyz)

        return xyz

    def get_scale(self):
        xyz = (1, 1, 1)

        self.put_scale(xyz)

        return xyz
