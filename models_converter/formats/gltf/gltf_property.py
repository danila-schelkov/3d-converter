from models_converter.utilities.math import Vector3, Quaternion
from models_converter.utilities.matrix.matrix4x4 import Matrix4x4


def to_camelcase(property_name: str):
    words = property_name.split('_')
    for word_index in range(len(words)):
        word = words[word_index]
        if word_index > 0:
            word = word.capitalize()
        words[word_index] = word
    camelcase_name = ''.join(words)
    return camelcase_name


def to_lowercase(property_name: str) -> str:
    result = ''

    for char in property_name:
        if char.isupper():
            char = f'_{char.lower()}'

        result += char

    return result


class GlTFProperty:
    def __init__(self):
        self.extensions = []
        self.extras = None

    def from_dict(self, dictionary: dict):
        if dictionary:
            for key, value in dictionary.items():
                attribute_name = to_lowercase(key)
                value_type = type(value)

                attribute_value = getattr(self, attribute_name)

                if attribute_value is None or value_type in (int, str, bool):
                    attribute_value = value
                elif type(attribute_value) in (Vector3, Quaternion, Matrix4x4) and type(value) is list:
                    attribute_value = type(attribute_value)(*value)
                elif issubclass(attribute_value, GlTFProperty):
                    if value_type is list:
                        value_type = attribute_value
                        values = []

                        for item in value:
                            new_value = value_type()
                            new_value.from_dict(item)

                            values.append(new_value)

                        attribute_value = values
                    else:
                        attribute_value = attribute_value()
                        attribute_value.from_dict(value)

                setattr(self, attribute_name, attribute_value)

    def to_dict(self) -> dict:
        dictionary = {}
        for key, value in self.__dict__.items():
            if value is not None:
                attribute_name = to_camelcase(key)
                value_type = type(value)

                attribute_value = None

                if value_type is list:
                    attribute_value = []
                    for item in value:
                        item_type = type(item)

                        if issubclass(item_type, GlTFProperty):
                            item = item.to_dict()
                        attribute_value.append(item)
                elif issubclass(value_type, GlTFProperty):
                    attribute_value = value.to_dict()
                elif attribute_value is None:
                    attribute_value = value

                dictionary[attribute_name] = attribute_value
        return dictionary

    def __getitem__(self, item):
        item = to_lowercase(item)
        if hasattr(self, item):
            return getattr(self, item)
        else:
            raise IndexError('The object has no attribute named ' + item)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} ({self.to_dict()})>'
