import abc

from models_converter.formats.universal import Scene


class WriterInterface:
    MAGIC: bytes

    @abc.abstractmethod
    def __init__(self):
        self.writen: bytes or str = None

    @abc.abstractmethod
    def write(self, scene: Scene):
        """

        :param scene:
        :return:
        """
