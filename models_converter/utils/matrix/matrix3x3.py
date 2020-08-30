from .matrix2x2 import Matrix2x2
from . import Matrix


class Matrix3x3(Matrix):
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

        matrix1 = Matrix2x2(matrix=(
            (value2_2, value2_3),
            (value3_2, value3_3)
        ))

        matrix2 = Matrix2x2(matrix=(
            (value2_1, value2_3),
            (value3_1, value3_3)
        ))

        matrix3 = Matrix2x2(matrix=(
            (value2_1, value2_2),
            (value3_1, value3_2)
        ))

        det = value1_1 * matrix1.determinant()
        det -= value1_2 * matrix2.determinant()
        det += value1_3 * matrix3.determinant()

        return det

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

        matrix1 = Matrix2x2(matrix=(
            (value2_2, value2_3),
            (value3_2, value3_3)
        ))
        matrix2 = Matrix2x2(matrix=(
            (value2_1, value2_3),
            (value3_1, value3_3)
        ))
        matrix3 = Matrix2x2(matrix=(
            (value2_1, value2_2),
            (value3_1, value3_2)
        ))
        matrix4 = Matrix2x2(matrix=(
            (value1_2, value1_3),
            (value3_2, value3_3)
        ))
        matrix5 = Matrix2x2(matrix=(
            (value1_1, value1_3),
            (value3_1, value3_3)
        ))
        matrix6 = Matrix2x2(matrix=(
            (value1_1, value1_2),
            (value3_1, value3_2)
        ))
        matrix7 = Matrix2x2(matrix=(
            (value1_2, value1_3),
            (value2_2, value2_3)
        ))
        matrix8 = Matrix2x2(matrix=(
            (value1_1, value1_3),
            (value2_1, value2_3)
        ))
        matrix9 = Matrix2x2(matrix=(
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
