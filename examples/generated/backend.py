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
        self.type = type

    def __sizeof__(self) -> int:
        return sizeof(self.type)

    @property
    def value(self) -> Any:
        value = self._mem_read(self.address, sizeof(self.type))
        return type.from_buffer_copy(value)

    @value.setter
    def value(self, arg) -> None:
        if not isinstance(arg, type):
            try:
                arg = type(arg)
            except TypeError:
                raise TypeError(f'Expected object of type {self.type}')

        value = bytes(arg)
        self._mem_write(self.address, value)


class Function(GeneratorFrontend):
    def __init__(self, address: int, arg_types: list[Type], return_type: Type) -> None:
        self.address = address
        self.arg_types = arg_types
        self.return_type = return_type

    def __call__(self, *args) -> Any:
        for idx, arg in enumerate(args):
            if not isinstance(arg, self.arg_types[idx]):
                try:
                    arg = type(arg)
                except TypeError:
                    raise TypeError(f'Expected object of type {self.arg_types[idx]}')

        value = self._exectue(self.address, args, sizeof(self.return_type))
        return self.return_type.from_buffer_copy(value)


class FunctionType(GeneratorFrontend):
    pass


class PointerClass():
    """Factory of pointer classes"""
    pass


class Enum(GeneratorFrontend):
    pass


class Void(GeneratorFrontend):
    """Dummy class for special cases"""
    pass
