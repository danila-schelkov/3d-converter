from typing import Literal


class Writer:
    def __init__(self, endian: Literal["little", "big"] = "big"):
        self.endian: Literal["little", "big"] = endian
        self.bit_shift = 0
        self.buffer = b""

    def write(self, data: bytes):
        self.buffer += data

    def write_unsigned_integer(self, integer: int, length: int = 1):
        self.write(integer.to_bytes(length, self.endian, signed=False))
        self.bit_shift = 0

    def write_integer(self, integer: int, length: int = 1):
        self.write(integer.to_bytes(length, self.endian, signed=True))
        self.bit_shift = 0

    def write_unsigned_int64(self, integer: int):
        self.write_unsigned_integer(integer, 8)

    def write_int64(self, integer: int):
        self.write_integer(integer, 8)

    def write_float(self, floating: float):
        exponent = 0
        sign = 1

        if floating == 0:
            self.write_unsigned_int32(0)
        else:
            if floating < 0:
                sign = -1
                floating = -floating

            if floating >= 2**-1022:
                value = floating

                while value < 1:
                    exponent -= 1
                    value *= 2
                while value >= 2:
                    exponent += 1
                    value /= 2

            mantissa = floating / 2**exponent

            exponent += 127

            as_integer_bin = "0"
            if sign == -1:
                as_integer_bin = "1"

            as_integer_bin += bin(exponent)[2:].zfill(8)

            mantissa_bin = ""
            for x in range(24):
                bit = "0"
                if mantissa >= 1 / 2**x:
                    mantissa -= 1 / 2**x
                    bit = "1"
                mantissa_bin += bit

            mantissa_bin = mantissa_bin[1:]

            as_integer_bin += mantissa_bin
            as_integer = int(as_integer_bin, 2)

            self.write_unsigned_int32(as_integer)

    def write_unsigned_int32(self, integer: int):
        self.write_unsigned_integer(integer, 4)

    def write_int32(self, integer: int):
        self.write_integer(integer, 4)

    def write_normalized_unsigned_int16(self, integer: int | float):
        self.write_unsigned_int16(int(integer * 65535))

    def write_unsigned_int16(self, integer: int):
        self.write_unsigned_integer(integer, 2)

    def write_normalized_int16(self, integer: int | float):
        self.write_int16(int(integer * 32512))

    def write_int16(self, integer: int):
        self.write_integer(integer, 2)

    def write_unsigned_int8(self, integer: int):
        self.write_unsigned_integer(integer)

    def write_int8(self, integer: int):
        self.write_integer(integer)

    def write_boolean(self, boolean: bool):
        if self.bit_shift == 0:
            self.write_unsigned_int8(0)

        if boolean:
            last_byte = self.buffer[len(self.buffer) - 1]
            self.buffer = self.buffer[:-1]
            self.write(
                (last_byte | (1 << self.bit_shift)).to_bytes(
                    1, self.endian, signed=False
                )
            )
        self.bit_shift = self.bit_shift + 1 & 7

    def write_string(self, string: str | None = None):
        if string is None:
            self.write_unsigned_int16(0xFFFF)
            return

        encoded = string.encode("utf-8")
        self.write_unsigned_int16(len(encoded))
        self.write(encoded)
