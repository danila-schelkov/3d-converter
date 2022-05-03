class Camera:
    def __init__(self, *, name: str, fov: float, aspect_ratio: float, near: float, far: float):
        self._name: str = name
        self._v1: float = 0
        self._fov: float = fov
        self._aspect_ratio: float = aspect_ratio
        self._near: float = near
        self._far: float = far

    def get_name(self) -> str:
        return self._name

    def get_v1(self) -> float:
        return self._v1

    def get_fov(self) -> float:
        return self._fov

    def get_aspect_ration(self) -> float:
        return self._aspect_ratio

    def get_near(self) -> float:
        return self._near

    def get_far(self) -> float:
        return self._far
