import json

from models_converter.interfaces import WriterInterface


class Writer(WriterInterface):
    MAGIC = b'glTF'

    def __init__(self):
        self.writen = self.MAGIC

        self.data = bytes()
        self.asset = {"version": "2.0"}
        self.scene = 0
        self.scenes = [{
            "nodes": []
        }]
        self.nodes = []
        self.buffers = []
        self.buffer_views = []
        self.accessors = []
        self.meshes = []
        self.materials = []
        self.textures = []
        self.images = []
        self.samplers = []

    def add_root_node_index(self, index):
        self.scenes[0]["nodes"].append(index)

    def add_node(self, node):
        self.nodes.append(node)

    def add_mesh(self, mesh):
        self.meshes.append(mesh)

    def add_material(self, material):
        self.materials.append(material)

    def add_texture(self, texture):
        self.textures.append(texture)

    def add_image(self, image):
        self.images.append(image)

    def add_sampler(self, sampler):
        self.samplers.append(sampler)

    def add_data(self, data):
        offset = len(self.data)
        self.data += data
        return offset

    def add_buffer_view(self, buffer_view):
        index = len(self.buffer_views)
        self.buffer_views.append(buffer_view)
        return index

    def add_accessor(self, accessor):
        index = len(self.accessors)
        self.accessors.append(accessor)
        return index

    def as_dict(self):
        return {
            "asset": self.asset,
            "scene": self.scene,
            "scenes": self.scenes,
            "nodes": self.nodes,
            "buffers": self.buffers,
            "bufferViews": self.buffer_views,
            "accessors": self.accessors,
            "meshes": self.meshes,
            "materials": self.materials,
            "textures": self.textures,
            "images": self.images,
            "samplers": self.samplers,
        }

    def write(self, data: dict):
        print(data)

        json_data = json.dumps(self.as_dict())

        self.buffers.append({
            "byteLength": len(self.data)
        })
        # pad json data with spaces
        json_data += " " * (4 - len(json_data) % 4)
        # pad binary data with null bytes
        self.data += bytes((4 - len(self.data) % 4))

        self.writen += (2).to_bytes(4, 'little')
        self.writen += (len(json_data) + len(self.data) + 28).to_bytes(4, 'little')
        self.writen += len(json_data).to_bytes(4, 'little') + b'JSON' + json_data.encode()
        self.writen += len(self.data).to_bytes(4, 'little') + b'BIN\x00' + self.data
