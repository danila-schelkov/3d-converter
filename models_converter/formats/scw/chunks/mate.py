from . import Chunk


class MATE(Chunk):
    def __init__(self, header: dict):
        super().__init__(header)
        self.chunk_name = 'MATE'

    def parse(self, buffer: bytes):
        super().parse(buffer)

        setattr(self, 'name', self.readString())
        setattr(self, 'shader', self.readString())
        setattr(self, 'v1', self.readUByte())

        effect = {}
        use_ambient_tex = self.readBool()
        if use_ambient_tex:
            ambient_tex = self.readString()
            effect['ambient'] = ambient_tex
        else:
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

        setattr(self, 'v2', self.readString())
        setattr(self, 'v3', self.readString())

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

        setattr(self, 'v4', self.readString())
        setattr(self, 'v5', self.readFloat())
        setattr(self, 'v6', self.readFloat())

        effect['lightmaps'] = {
            'diffuse': self.readString(),
            'specular': self.readString()
        }

        a = self.readUByte()
        r = self.readUByte()
        g = self.readUByte()
        b = self.readUByte()
        effect['tint'] = (r, g, b, a)

        setattr(self, 'effect', effect)

    def encode(self):
        super().encode()

        self.length = len(self.buffer)

