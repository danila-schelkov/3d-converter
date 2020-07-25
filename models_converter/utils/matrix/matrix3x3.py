from .matrix2x2 import Matrix2x2


def matrix2tuple(matrix_list: list):
    new_matrix = [tuple(row) for row in matrix_list]
    new_matrix = tuple(new_matrix)

    return new_matrix


class Matrix3x3(object):
    def __init__(self, matrix_list: tuple = None):
        if matrix_list is not None:
            self.matrix = matrix_list
        else:
            self.matrix = (
                (1, 0, 0),  # x
                (0, 1, 0),  # y
                (0, 0, 1)  # z
            )

    def __matmul__(self, other):
        if len(self.matrix) != len(other.matrix[0]) or len(self.matrix[0]) != len(other.matrix):
            raise TypeError('Матрицы не могут быть перемножены')
        else:
            multiplied_matrix = []

            for row in self.matrix:
                matrix_row = []
                for column in range(3):
                    s = 0
                    for i in range(3):
                        s += row[i] * other.matrix[i][column]
                    matrix_row.append(s)
                multiplied_matrix.append(matrix_row)

            return Matrix3x3(matrix2tuple(multiplied_matrix))

    def __mul__(self, other: int or float):
        new_matrix = []
        for row in range(len(self.matrix)):
            new_row = []
            for column in range(len(self.matrix[0])):
                new_row.append(self.matrix[row][column]*other)
            new_matrix.append(new_row)

        return Matrix3x3(matrix2tuple(new_matrix))

    def inverse(self):
        det = self.determinant()
        if det != 0:
            self.transpose()
            self.cofactor()

            self.matrix = self.__mul__(1 / det).matrix

        return self

    def __str__(self):
        return str(self.matrix)

    def determinant(self):
        value1_1 = self.matrix[0][0]
        value1_2 = self.matrix[0][1]
        value1_3 = self.matrix[0][2]

        value2_1 = self.matrix[1][0]
        value2_2 = self.matrix[1][1]
        value2_3 = self.matrix[1][2]

        value3_1 = self.matrix[2][0]
        value3_2 = self.matrix[2][1]
        value3_3 = self.matrix[2][2]

        matrix1 = Matrix2x2((
            (value2_2, value2_3),
            (value3_2, value3_3)
        ))

        matrix2 = Matrix2x2((
            (value2_1, value2_3),
            (value3_1, value3_3)
        ))

        matrix3 = Matrix2x2((
            (value2_1, value2_2),
            (value3_1, value3_2)
        ))

        det = value1_1 * matrix1.determinant()
        det -= value1_2 * matrix2.determinant()
        det += value1_3 * matrix3.determinant()

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

        value2_1 = self.matrix[1][0]
        value2_2 = self.matrix[1][1]
        value2_3 = self.matrix[1][2]

        value3_1 = self.matrix[2][0]
        value3_2 = self.matrix[2][1]
        value3_3 = self.matrix[2][2]

        matrix1 = Matrix2x2((
            (value2_2, value2_3),
            (value3_2, value3_3)
        ))
        matrix2 = Matrix2x2((
            (value2_1, value2_3),
            (value3_1, value3_3)
        ))
        matrix3 = Matrix2x2((
            (value2_1, value2_2),
            (value3_1, value3_2)
        ))
        matrix4 = Matrix2x2((
            (value1_2, value1_3),
            (value3_2, value3_3)
        ))
        matrix5 = Matrix2x2((
            (value1_1, value1_3),
            (value3_1, value3_3)
        ))
        matrix6 = Matrix2x2((
            (value1_1, value1_2),
            (value3_1, value3_2)
        ))
        matrix7 = Matrix2x2((
            (value1_2, value1_3),
            (value2_2, value2_3)
        ))
        matrix8 = Matrix2x2((
            (value1_1, value1_3),
            (value2_1, value2_3)
        ))
        matrix9 = Matrix2x2((
            (value1_1, value1_2),
            (value2_1, value2_2)
        ))

        self.matrix = (
            (matrix1.determinant(), matrix2.determinant(), matrix3.determinant()),
            (matrix4.determinant(), matrix5.determinant(), matrix6.determinant()),
            (matrix7.determinant(), matrix8.determinant(), matrix9.determinant())
        )

        cofactor_matrix = []
        for row in range(len(self.matrix)):
            new_row = []
            for column in range(len(self.matrix[0])):
                new_row.append(self.matrix[row][column] * (-1) ** (row + column))
            cofactor_matrix.append(new_row)
        self.matrix = cofactor_matrix

