from . import Chunk
from ...universal.material import Material


class MATE(Chunk):
    def __init__(self, header):
        super().__init__(header)
        self.chunk_name = 'MATE'

        self.material = Material(name='default_material', shader=None, effect=Material.Effect)

    def parse(self, buffer: bytes):
        super().parse(buffer)

        self.material.set_name(self.readString())
        self.material.set_shader(self.readString())

        setattr(self, 'v1', self.readUByte())
        setattr(self, 'v2', self.readUByte())

        effect = {}
        a = self.readUByte()
        r = self.readUByte()
        g = self.readUByte()
        b = self.readUByte()
        ambient_color = (r, g, b, a)
        effect['ambient'] = ambient_color

        use_diffuse_tex = self.readBool()
        if use_diffuse_tex:
            diffuse_tex = self.readString()
            effect['diffuse'] = diffuse_tex
        else:
            a = self.readUByte()
            r = self.readUByte()
            g = self.readUByte()
            b = self.readUByte()
            diffuse_color = (r, g, b, a)
            effect['diffuse'] = diffuse_color

        use_specular_tex = self.readBool()
        if use_specular_tex:
            specular_tex = self.readString()
            effect['specular'] = specular_tex
        else:
            a = self.readUByte()
            r = self.readUByte()
            g = self.readUByte()
            b = self.readUByte()
            specular_color = (r, g, b, a)
            effect['specular'] = specular_color

        setattr(self, 'v3', self.readString())
        setattr(self, 'v4', self.readString())

        use_colorize_tex = self.readBool()
        if use_colorize_tex:
            colorize_tex = self.readString()
            effect['colorize'] = colorize_tex
        else:
            a = self.readUByte()
            r = self.readUByte()
            g = self.readUByte()
            b = self.readUByte()
            colorize_color = (r, g, b, a)
            effect['colorize'] = colorize_color

        use_emission_tex = self.readBool()
        if use_emission_tex:
            emission_tex = self.readString()
            effect['emission'] = emission_tex
        else:
            a = self.readUByte()
            r = self.readUByte()
            g = self.readUByte()
            b = self.readUByte()
            emission_color = (r, g, b, a)
            effect['emission'] = emission_color

        setattr(self, 'opacity_texture', self.readString())
        setattr(self, 'v5', self.readFloat())
        setattr(self, 'v6', self.readFloat())

        effect['lightmaps'] = {
            'diffuse': self.readString(),
            'specular': self.readString()
        }

        if self.header.version == 2:
            setattr(self, 'v7', self.readString())

        shader_define_flags = self.readUInt32()
        effect['shader_define_flags'] = shader_define_flags

        if shader_define_flags & 32768:
            self.readFloat()
            self.readFloat()
            self.readFloat()
            self.readFloat()

        setattr(self, 'effect', effect)

    def encode(self):
        super().encode()

        self.writeString(getattr(self, 'name'))
        self.writeString(getattr(self, 'shader'))
        self.writeUByte(4)  # getattr(self, 'v1')
        self.writeUByte(0)  # getattr(self, 'v2')

        effect = getattr(self, 'effect')
        r, g, b, a = effect['ambient']
        self.writeUByte(a)
        self.writeUByte(r)
        self.writeUByte(g)
        self.writeUByte(b)

        use_diffuse_tex = type(effect['diffuse']) is str
        self.writeBool(use_diffuse_tex)
        if use_diffuse_tex:
            self.writeString(effect['diffuse'])
        else:
            r, g, b, a = effect['diffuse']
            self.writeUByte(a)
            self.writeUByte(r)
            self.writeUByte(g)
            self.writeUByte(b)

        use_specular_tex = type(effect['specular']) is str
        self.writeBool(use_specular_tex)
        if use_specular_tex:
            self.writeString(effect['specular'])
        else:
            r, g, b, a = effect['specular']
            self.writeUByte(a)
            self.writeUByte(r)
            self.writeUByte(g)
            self.writeUByte(b)

        self.writeString('.')  # getattr(self, 'v3')
        self.writeString('')  # getattr(self, 'v4')

        use_colorize_tex = type(effect['colorize']) is str
        self.writeBool(use_colorize_tex)
        if use_colorize_tex:
            self.writeString(effect['colorize'])
        else:
            r, g, b, a = effect['colorize']
            self.writeUByte(a)
            self.writeUByte(r)
            self.writeUByte(g)
            self.writeUByte(b)

        use_emission_tex = type(effect['emission']) is str
        self.writeBool(use_emission_tex)
        if use_emission_tex:
            self.writeString(effect['emission'])
        else:
            r, g, b, a = effect['emission']
            self.writeUByte(a)
            self.writeUByte(r)
            self.writeUByte(g)
            self.writeUByte(b)

        self.writeString('')  # getattr(self, 'opacity_texture')
        self.writeFloat(1)  # getattr(self, 'v5')
        self.writeFloat(0)  # getattr(self, 'v6')

        self.writeString(effect['lightmaps']['diffuse'])
        self.writeString(effect['lightmaps']['specular'])

        if self.header['version'] == 2:
            self.writeString('')  # getattr(self, 'v7')

        self.writeUInt32(effect['shader_define_flags'])

        self.length = len(self.buffer)

