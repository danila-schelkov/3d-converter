class Matrix(object):
    def __init__(self, matrix_list: list = None):
        self.translation_matrix = None
        self.rotation_matrix = None
        self.scale_matrix = None

        if matrix_list is not None:
            self.matrix = matrix_list
        else:
            self.matrix = [
                [1, 0, 0, 0],  # x
                [0, 1, 0, 0],  # y
                [0, 0, 1, 0],  # z
                [0, 0, 0, 1]
            ]

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

            self.matrix = multiplied_matrix

            return self

    def __str__(self):
        return str(self.matrix)

    def write_rotation(self, xyz: tuple, angle: int):
        x, y, z = xyz

        rotation_matrix = [
            [1 - 2 * y ** 2 - 2 * z ** 2, 2 * x * y - 2 * z * angle, 2 * x * z + 2 * y * angle, 0],
            [2 * x * y + 2 * z * angle, 1 - 2 * x ** 2 - 2 * z ** 2, 2 * y * z - 2 * x * angle, 0],
            [2 * x * z - 2 * y * angle, 2 * y * z + 2 * x * angle, 1 - 2 * x ** 2 - 2 * y ** 2, 0],
            [0, 0, 0, 1]
        ]

        self.rotation_matrix = Matrix(rotation_matrix)

    def write_position(self, xyz: tuple):
        x, y, z = xyz

        translation_matrix = [
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]
        ]

        self.translation_matrix = Matrix(translation_matrix)

    def write_scale(self, xyz: tuple):
        x, y, z = xyz

        scale_matrix = [
            [x, 0, 0, 0],
            [0, y, 0, 0],
            [0, 0, z, 0],
            [0, 0, 0, 1]
        ]

        self.scale_matrix = Matrix(scale_matrix)


if __name__ == '__main__':
    matrix: Matrix = Matrix()

    matrix.write_position((0, 0, 0))
    matrix.write_rotation((0, 0, 1), 1)
    matrix.write_scale((0.9, 0.9, 0.9))

    matrix = matrix.translation_matrix @ matrix.rotation_matrix @ matrix.scale_matrix
    print(matrix)
