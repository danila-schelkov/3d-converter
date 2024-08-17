from typing import Literal


class Reader:
    def __init__(self, buffer: bytes, endian: Literal["big", "little"]):
        self.buffer = buffer
        self.endian = endian
        self.bit_shift = 0
        self.i = 0

    def read(self, length: int = 1) -> bytes:
        result = self.buffer[self.i : self.i + length]
        self.i += length

        return result

    def read_unsigned_integer(self, length: int = 1) -> int:
        self.flush_bit_state()

        result = 0
        for x in range(length):
            byte = self.buffer[self.i]

            bit_padding = x * 8
            if self.endian == "big":
                bit_padding = (8 * (length - 1)) - bit_padding

            result |= byte << bit_padding
            self.i += 1

        return result

    def read_integer(self, length: int = 1) -> int:
        integer = self.read_unsigned_integer(length)
        result = integer
        if integer > 2 ** (length * 8) / 2:
            result -= 2 ** (length * 8)
        return result

    def read_unsigned_int64(self) -> int:
        return self.read_unsigned_integer(8)

    def read_int64(self) -> int:
        return self.read_integer(8)

    def read_float(self) -> float:
        as_int = self.read_unsigned_int32()
        binary = bin(as_int)
        binary = binary[2:].zfill(32)

        sign = -1 if binary[0] == "1" else 1
        exponent = int(binary[1:9], 2) - 127
        mantissa_base = binary[9:]
        mantissa_bin = "1" + mantissa_base
        mantissa = 0
        val = 1

        if exponent == -127:
            if mantissa_base[1] == -1:
                return 0
            else:
                exponent = -126
                mantissa_bin = "0" + mantissa_base

        for char in mantissa_bin:
            mantissa += val * int(char)
            val = val / 2

        result = sign * 2**exponent * mantissa
        return result

    def read_unsigned_int32(self) -> int:
        return self.read_unsigned_integer(4)

    def read_int32(self) -> int:
        return self.read_integer(4)

    def read_normalized_unsigned_int16(self) -> float:
        return self.read_unsigned_int16() / 65535

    def read_unsigned_int16(self) -> int:
        return self.read_unsigned_integer(2)

    def read_normalized_int16(self) -> float:
        return self.read_int16() / 32512

    def read_int16(self) -> int:
        return self.read_integer(2)

    def read_unsigned_int8(self) -> int:
        return self.read_unsigned_integer()

    def read_int8(self) -> int:
        return self.read_integer()

    def read_boolean(self) -> bool:
        current_byte = self.buffer[self.i]
        boolean = current_byte & 2**self.bit_shift

        self.bit_shift += 1 & 7
        if self.bit_shift == 0:
            self.i += 1
        if boolean == 1:
            return True
        return False

    def read_char(self, length: int = 1) -> str:
        return self.read(length).decode("utf-8")

    def read_string(self) -> str | None:
        length = self.read_unsigned_int16()
        if length == 0xFF:
            return None

        return self.read_char(length)

    def tell(self) -> int:
        return self.i

    def flush_bit_state(self):
        if self.bit_shift > 0:
            self.bit_shift = 0
            self.i += 1
