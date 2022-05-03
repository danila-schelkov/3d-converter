from models_converter.formats.universal import Scene


class WriterInterface:
    MAGIC: bytes

    def __init__(self):
        self.writen: bytes or str = None

        raise NotImplementedError('This is an abstract class')

    def write(self, scene: Scene):
        raise NotImplementedError('This is an abstract class')
