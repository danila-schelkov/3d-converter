class Vector3:
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        self.x = x
        self.y = y
        self.z = z

    def clone(self):
        return Vector3(self.x, self.y, self.z)

    def __repr__(self):
        return f'({self.x:.2f}, {self.y:.2f}, {self.z:.2f})'
