class Matrix:
    def __init__(self, **kwargs):
        matrix = None

        if 'matrix' in kwargs:
            matrix = kwargs['matrix']

        if 'size' in kwargs:
            self.size = kwargs['size']

            matrix = self.get_identity_matrix(
                self.size
            )
        else:
            self.size = (
                len(matrix[0]),  # x
                len(matrix)  # y
            )

        self.matrix = matrix

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

            return Matrix(matrix=multiplied_matrix)

    def __mul__(self, other: int or float):
        multiplied_matrix = []
        for row in range(len(self.matrix)):
            new_row = []
            for column in range(len(self.matrix[0])):
                new_row.append(self.matrix[row][column]*other)
            multiplied_matrix.append(new_row)

        return Matrix(matrix=multiplied_matrix)

    def __repr__(self):
        return f'{self.__class__.__name__} <{self.matrix}>'

    def __str__(self):
        return str(self.matrix)

    @staticmethod
    def get_identity_matrix(size: tuple):
        matrix = []

        for y in range(size[1]):
            row = []
            for x in range(size[0]):
                element = 0
                if x == y:
                    element = 1
                row.append(element)
            matrix.append(row)

        return matrix

    def find_cofactor(self):
        cofactor_matrix = []

        for row in range(len(self.matrix)):
            new_row = []
            for column in range(len(self.matrix[0])):
                new_row.append(self.matrix[row][column] * (-1) ** (row + column))
            cofactor_matrix.append(new_row)

        self.matrix = cofactor_matrix

    def transpose(self):
        height = len(self.matrix)
        width = len(self.matrix[0])

        self.matrix = [[self.matrix[row][col] for row in range(height)] for col in range(width)]
        self.matrix = [tuple(row) for row in self.matrix]
        self.matrix = tuple(self.matrix)

    def determinant(self):
        det = 0

        return det

    def cofactor(self):
        pass

    def inverse(self):
        det = self.determinant()
        if det != 0:
            self.transpose()
            self.cofactor()

            self.matrix = self.__mul__(1 / det).matrix

        return self


__all__ = [
    'matrix2x2',
    'matrix3x3',
    'matrix4x4'
]
