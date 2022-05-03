from xml.etree.ElementTree import *


VERSION = '1.4.1'
NAMESPACE = 'http://www.collada.org/2005/11/COLLADASchema'


class Collada:
    def __init__(self):
        self.root = Element('COLLADA', version=VERSION, xmlns=NAMESPACE)

    @staticmethod
    def write_source(parent,
                     source_id: str,
                     array_tag: str,
                     array_data: tuple,
                     stride: int,
                     params: list):
        source = SubElement(parent, 'source', id=source_id)

        array = SubElement(source, array_tag)
        array.attrib = {'id': f'{source_id}-array',
                        'count': f'{len(array_data) * stride}'}

        technique_common = SubElement(source, 'technique_common')
        accessor = SubElement(technique_common, 'accessor')
        accessor.attrib = {'source': f'#{source_id}-array',
                           'count': f'{len(array_data)}',
                           'stride': f'{stride}'}

        for param_data in params:
            param = SubElement(accessor, 'param')
            param.attrib = param_data

        array.text = ' '.join(array_data)

    @staticmethod
    def write_input(parent,
                    semantic: str,
                    source_id: str,
                    offset: int = None):
        attributes = {
            'semantic': semantic,
            'source': f'#{source_id}'
        }

        if offset is not None:
            attributes['offset'] = f'{offset}'

        _input = SubElement(parent, 'input')
        _input.attrib = attributes
