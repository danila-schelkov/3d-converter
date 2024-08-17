import abc

from models_converter.formats.universal import Scene


class ParserInterface:
    @abc.abstractmethod
    def __init__(self, file_data: bytes | str):
        self.scene: Scene | None = None

    @abc.abstractmethod
    def parse(self):
        """

        :return:
        """
