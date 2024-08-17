from typing import ClassVar

from . import Chunk


class WEND(Chunk):
    chunk_name: ClassVar[str] = "WEND"
