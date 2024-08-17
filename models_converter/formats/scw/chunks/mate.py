from __future__ import annotations

from typing import TYPE_CHECKING, cast

from . import Chunk
from ...universal.material import Material

if TYPE_CHECKING:
    from models_converter.formats.scw.chunks import HEAD


class MATE(Chunk):
    chunk_name = "MATE"

    def __init__(self, material: Material | None = None):
        self.material = Material(
            name="default_material", shader=None, effect=Material.Effect()
        )

    def parse(self, buffer: bytes, header: HEAD | None = None) -> None:
        super().parse(buffer)

        assert header is not None

        self.material.set_name(cast(str, self.read_string()))
        self.material.set_shader(self.read_string())

        setattr(self, "v1", self.read_unsigned_int8())
        setattr(self, "v2", self.read_unsigned_int8())

        effect = {}
        ambient_color = self._read_color_rgba()
        effect["ambient"] = ambient_color

        use_diffuse_tex = self.read_boolean()
        if use_diffuse_tex:
            diffuse_tex = self.read_string()
            effect["diffuse"] = diffuse_tex
        else:
            diffuse_color = self._read_color_rgba()
            effect["diffuse"] = diffuse_color

        use_specular_tex = self.read_boolean()
        if use_specular_tex:
            specular_tex = self.read_string()
            effect["specular"] = specular_tex
        else:
            specular_color = self._read_color_rgba()
            effect["specular"] = specular_color

        setattr(self, "v3", self.read_string())
        setattr(self, "v4", self.read_string())

        use_colorize_tex = self.read_boolean()
        if use_colorize_tex:
            colorize_tex = self.read_string()
            effect["colorize"] = colorize_tex
        else:
            colorize_color = self._read_color_rgba()
            effect["colorize"] = colorize_color

        use_emission_tex = self.read_boolean()
        if use_emission_tex:
            emission_tex = self.read_string()
            effect["emission"] = emission_tex
        else:
            emission_color = self._read_color_rgba()
            effect["emission"] = emission_color

        setattr(self, "opacity_texture", self.read_string())
        setattr(self, "v5", self.read_float())
        setattr(self, "v6", self.read_float())

        effect["lightmaps"] = {
            "diffuse": self.read_string(),
            "specular": self.read_string(),
        }

        if header.version == 2:
            setattr(self, "v7", self.read_string())

        shader_define_flags = self.read_unsigned_int32()
        effect["shader_define_flags"] = shader_define_flags

        if shader_define_flags & 32768:
            self.read_float()
            self.read_float()
            self.read_float()
            self.read_float()

        setattr(self, "effect", effect)

    def _read_color_rgba(self) -> tuple[int, int, int, int]:
        a = self.read_unsigned_int8()
        r = self.read_unsigned_int8()
        g = self.read_unsigned_int8()
        b = self.read_unsigned_int8()
        return r, g, b, a

    def encode(self, header) -> None:
        super().encode()

        self.write_string(getattr(self, "name"))
        self.write_string(getattr(self, "shader"))
        self.write_unsigned_int8(4)  # getattr(self, 'v1')
        self.write_unsigned_int8(0)  # getattr(self, 'v2')

        effect = getattr(self, "effect")
        r, g, b, a = effect["ambient"]
        self.write_unsigned_int8(a)
        self.write_unsigned_int8(r)
        self.write_unsigned_int8(g)
        self.write_unsigned_int8(b)

        use_diffuse_tex = type(effect["diffuse"]) is str
        self.write_boolean(use_diffuse_tex)
        if use_diffuse_tex:
            self.write_string(effect["diffuse"])
        else:
            r, g, b, a = effect["diffuse"]
            self.write_unsigned_int8(a)
            self.write_unsigned_int8(r)
            self.write_unsigned_int8(g)
            self.write_unsigned_int8(b)

        use_specular_tex = type(effect["specular"]) is str
        self.write_boolean(use_specular_tex)
        if use_specular_tex:
            self.write_string(effect["specular"])
        else:
            r, g, b, a = effect["specular"]
            self.write_unsigned_int8(a)
            self.write_unsigned_int8(r)
            self.write_unsigned_int8(g)
            self.write_unsigned_int8(b)

        self.write_string(".")  # getattr(self, 'v3')
        self.write_string("")  # getattr(self, 'v4')

        use_colorize_tex = type(effect["colorize"]) is str
        self.write_boolean(use_colorize_tex)
        if use_colorize_tex:
            self.write_string(effect["colorize"])
        else:
            r, g, b, a = effect["colorize"]
            self.write_unsigned_int8(a)
            self.write_unsigned_int8(r)
            self.write_unsigned_int8(g)
            self.write_unsigned_int8(b)

        use_emission_tex = type(effect["emission"]) is str
        self.write_boolean(use_emission_tex)
        if use_emission_tex:
            self.write_string(effect["emission"])
        else:
            r, g, b, a = effect["emission"]
            self.write_unsigned_int8(a)
            self.write_unsigned_int8(r)
            self.write_unsigned_int8(g)
            self.write_unsigned_int8(b)

        self.write_string("")  # getattr(self, 'opacity_texture')
        self.write_float(1)  # getattr(self, 'v5')
        self.write_float(0)  # getattr(self, 'v6')

        self.write_string(effect["lightmaps"]["diffuse"])
        self.write_string(effect["lightmaps"]["specular"])

        if header["version"] == 2:
            self.write_string("")  # getattr(self, 'v7')

        self.write_unsigned_int32(effect["shader_define_flags"])

        self.length = len(self.buffer)
