from ..utils.reader import Reader
from ..utils.writer import Writer


class Decoder(Reader):
    def __init__(self, initial_bytes: bytes, header: dict):
        super().__init__(initial_bytes)

        self.readed = {}

        name = self.readString()
        shader = self.readString()
        self.readUByte()
        self.readed['name'] = name
        self.readed['shader'] = shader

        self.readed['effect'] = {}
        use_ambient_tex = self.readBool()
        if use_ambient_tex:
            ambient_tex = self.readString()
            self.readed['effect']['ambient'] = ambient_tex
        else:
            a = self.readUByte()
            r = self.readUByte()
            g = self.readUByte()
            b = self.readUByte()
            ambient_color = (r, g, b, a)
            self.readed['effect']['ambient'] = ambient_color

        use_diffuse_tex = self.readBool()
        if use_diffuse_tex:
            diffuse_tex = self.readString()
            self.readed['effect']['diffuse'] = diffuse_tex
        else:
            a = self.readUByte()
            r = self.readUByte()
            g = self.readUByte()
            b = self.readUByte()
            diffuse_color = (r, g, b, a)
            self.readed['effect']['diffuse'] = diffuse_color

        use_specular_tex = self.readBool()
        if use_specular_tex:
            specular_tex = self.readString()
            self.readed['effect']['specular'] = specular_tex
        else:
            a = self.readUByte()
            r = self.readUByte()
            g = self.readUByte()
            b = self.readUByte()
            specular_color = (r, g, b, a)
            self.readed['effect']['specular'] = specular_color

        texture_one = self.readString()
        texture_two = self.readString()

        use_colorize_tex = self.readBool()
        if use_colorize_tex:
            colorize_tex = self.readString()
            self.readed['effect']['colorize'] = colorize_tex
        else:
            a = self.readUByte()
            r = self.readUByte()
            g = self.readUByte()
            b = self.readUByte()
            colorize_color = (r, g, b, a)
            self.readed['effect']['colorize'] = colorize_color

        use_emission_tex = self.readBool()
        if use_emission_tex:
            emission_tex = self.readString()
            self.readed['effect']['emission'] = emission_tex
        else:
            a = self.readUByte()
            r = self.readUByte()
            g = self.readUByte()
            b = self.readUByte()
            emission_color = (r, g, b, a)
            self.readed['effect']['emission'] = emission_color

        self.readString()
        self.readFloat()
        self.readFloat()

        lightmap_diffuse_tex = self.readString()
        lightmap_specular_tex = self.readString()
        self.readed['effect']['lightmaps'] = {
            'diffuse': lightmap_diffuse_tex,
            'specular': lightmap_specular_tex
        }

        a = self.readUByte()
        r = self.readUByte()
        g = self.readUByte()
        b = self.readUByte()
        tint = (r, g, b, a)
        self.readed['effect']['tint'] = tint


class Encoder(Writer):
    def __init__(self, data: dict):
        super().__init__()
        self.name = 'MATE'
        self.data = data

        self.encode()

        self.length = len(self.buffer)

    def encode(self):
        pass
