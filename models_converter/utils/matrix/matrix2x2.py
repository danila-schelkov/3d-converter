def matrix2tuple(matrix_list: list):
    new_matrix = [tuple(row) for row in matrix_list]
    new_matrix = tuple(new_matrix)

    return new_matrix


class Matrix2x2(object):
    def __init__(self, matrix_list: tuple = None):
        if matrix_list is not None:
            self.matrix = matrix_list
        else:
            self.matrix = (
                (1, 0),  # x
                (0, 1),  # y
            )

    def __matmul__(self, other):
        if len(self.matrix) != len(other.matrix[0]) or len(self.matrix[0]) != len(other.matrix):
            raise TypeError('Матрицы не могут быть перемножены')
        else:
            multiplied_matrix = []

            for row in self.matrix:
                matrix_row = []
                for column in range(2):
                    s = 0
                    for i in range(2):
                        s += row[i] * other.matrix[i][column]
                    matrix_row.append(s)
                multiplied_matrix.append(matrix_row)

            return Matrix2x2(matrix2tuple(multiplied_matrix))

    def __mul__(self, other: int or float):
        new_matrix = []
        for row in range(len(self.matrix)):
            new_row = []
            for column in range(len(self.matrix[0])):
                new_row.append(self.matrix[row][column]*other)
            new_matrix.append(new_row)

        return Matrix2x2(matrix2tuple(new_matrix))

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

        value2_1 = self.matrix[1][0]
        value2_2 = self.matrix[1][1]

        det = value1_1 * value2_2
        det -= value1_2 * value2_1

        return det

    def transpose(self):
        value1_1 = self.matrix[0][0]
        value1_2 = self.matrix[0][1]

        value2_1 = self.matrix[1][0]
        value2_2 = self.matrix[1][1]

        self.matrix = (
            (value2_2, value1_2),
            (value2_1, value1_1)
        )

    def cofactor(self):
        cofactor_matrix = []
        for row in range(len(self.matrix)):
            new_row = []
            for column in range(len(self.matrix[0])):
                new_row.append(self.matrix[row][column] * (-1) ** (row + column))
            cofactor_matrix.append(new_row)
        self.matrix = cofactor_matrix

