from abc import ABC, abstractmethod
from ctypes import sizeof
from typing import Any, Type


class GeneratorFrontend(ABC):
    """Class dictates how testing framework communicates with device

        - MemoryAccess - class that implements methods
            - memory_read(address, size) - read size bytes from given address
            - memory_write(address, bytes) - write to memory under given address
            - execute(address, args, ret_size) - execute memory under given address with given args, expect given respone size"""

    MemoryAccess = None

    @abstractmethod
    def __init__(): ...

    def _mem_write(self, address, bytes) -> None:
        self.MemoryAccess.memory_write(address, bytes)

    def _mem_read(self, address, size) -> bytes:
        return self.MemoryAccess.memory_read(address, size)

    def _exectue(self, address, args, ret_size) -> bytes:
        self.MemoryAccess.execute(address, args, ret_size)


class Variable(GeneratorFrontend):
    def __init__(self, address: int, type: Type) -> None:
        self.address = address

    def __sizeof__(self) -> int:
        return sizeof(self.type)

    @property
    def value(self) -> Any:
        pass

    @value.setter
    def value(self, arg) -> None:
        pass


class Function(GeneratorFrontend):
    def __init__(self, address: int, arg_types: list[Type], return_type: Type) -> None:
        self.address = address

    def __sizeof__(self) -> int:
        return sizeof(self.type)

    @property
    def value(self) -> Any:
        pass

    @value.setter
    def value(self, arg) -> None:
        pass


class FunctionType(GeneratorFrontend):
    pass


class VoidPointer(GeneratorFrontend):
    pass


class Pointer(GeneratorFrontend):
    pass


class Enum(GeneratorFrontend):
    pass
