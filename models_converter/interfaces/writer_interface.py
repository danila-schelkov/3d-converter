import abc

from models_converter.formats.universal import Scene


class WriterInterface(abc.ABC):
    MAGIC: bytes

    @abc.abstractmethod
    def __init__(self):
        self.writen: bytes | str = b""

    @abc.abstractmethod
    def write(self, scene: Scene):
        """

        :param scene:
        :return:
        """
