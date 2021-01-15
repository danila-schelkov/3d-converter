from ....utils.reader import Reader
from ....utils.writer import Writer


class Chunk(Writer, Reader):
    def __init__(self, header=None):
        super().__init__()

        if header is None:
            header = {}

        self.header = header
        self.chunk_name = ''

        self.buffer = b''
        self.length = 0

    def from_dict(self, dictionary: dict):
        if dictionary:
            for key, value in dictionary.items():
                setattr(self, key, value)

    def to_dict(self) -> dict:
        dictionary = {}
        for key, value in self.__dict__.items():
            if key in ['header', 'buffer', 'length', 'endian', 'i']:
                continue
            if value is not None:
                attribute_name = key
                value_type = type(value)

                attribute_value = None

                if value_type is list:
                    attribute_value = []
                    for item in value:
                        item_type = type(item)

                        if issubclass(item_type, Chunk):
                            item = item.to_dict()
                        attribute_value.append(item)
                elif issubclass(value_type, Chunk):
                    attribute_value = value.to_dict()
                elif attribute_value is None:
                    attribute_value = value

                dictionary[attribute_name] = attribute_value
        return dictionary

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            raise IndexError('The object has no attribute named ' + key)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} ({self.to_dict()})>'

    def set(self, key: str, value):
        setattr(self, key, value)

    def parse(self, buffer: bytes):
        Reader.__init__(self, buffer, 'big')

    def encode(self):
        Writer.__init__(self, 'big')

        self.length = len(self.buffer)

    get = __getitem__
