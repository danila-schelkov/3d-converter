from . import Matrix


class Matrix2x2(Matrix):
    def determinant(self):
        value1_1 = self.matrix[0][0]
        value1_2 = self.matrix[0][1]

        value2_1 = self.matrix[1][0]
        value2_2 = self.matrix[1][1]

        det = value1_1 * value2_2
        det -= value1_2 * value2_1

        return det

    def cofactor(self):
        self.find_cofactor()
