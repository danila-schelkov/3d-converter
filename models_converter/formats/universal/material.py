class Material:
    class Effect:
        pass

    def __init__(self, *, name: str, shader: str | None, effect: Effect):
        self._name: str = name
        self._shader: str | None = shader
        self._effect: Material.Effect = effect

    def get_name(self) -> str:
        return self._name

    def set_name(self, name: str):
        self._name = name

    def get_shader(self) -> str | None:
        return self._shader

    def set_shader(self, shader: str | None):
        self._shader = shader

    def get_effect(self) -> Effect:
        return self._effect
