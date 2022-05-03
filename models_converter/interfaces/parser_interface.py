from models_converter.formats.universal import Scene


class ParserInterface:
    def __init__(self):
        self.scene: Scene or None = None

        raise NotImplementedError('This is an abstract class')

    def parse(self):
        raise NotImplementedError('This is an abstract class')
