class Quaternion:
    def __init__(self, x: float = 0, y: float = 0, z: float = 0, w: float = 1):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def clone(self):
        return Quaternion(self.x, self.y, self.z, self.w)
