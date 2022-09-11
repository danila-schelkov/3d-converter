class Quaternion:
    def __init__(self, x: float = 0, y: float = 0, z: float = 0, w: float = 1):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def clone(self):
        return Quaternion(self.x, self.y, self.z, self.w)

    def __repr__(self):
        return f'({self.x:.2f}, {self.y:.2f}, {self.z:.2f}, {self.w:.2f})'
