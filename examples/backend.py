from abc import ABC, abstractmethod
from ctypes import sizeof, Structure, Union, c_uint32, c_uint64
from typing import Any, Type

MACHINE_ADDR_SIZE = 8

ADDR_SIZE_MAP: dict[int, type] = {
    4: c_uint32,
    8: c_uint64
}


class GeneratorBackend(ABC):
    """Class dictates how testing framework communicates with device

        - MemoryAccess - class that implements methods
            - memory_read(address, size) - read size bytes from given address
            - memory_write(address, bytes) - write to memory under given address
            - execute(address, args, ret_size) - execute memory under given address with given args, expect given respone size
    """

    MemoryAccess = None

    @abstractmethod
    def __init__(): ...

    def _mem_write(self, address, bytes) -> None:
        GeneratorBackend.MemoryAccess.memory_write(address, bytes)

    def _mem_read(self, address, size) -> bytes:
        return GeneratorBackend.MemoryAccess.memory_read(address, size)

    def _exectue(self, address, args, ret_size) -> bytes:
        GeneratorBackend.MemoryAccess.execute(address, args, ret_size)


class Variable(GeneratorBackend):
    def __init__(self, address: int, type: Type) -> None:
        self.address = address
        self.type = type

    def __sizeof__(self) -> int:
        return sizeof(self.type)

    @property
    def value(self) -> Any:
        value = self._mem_read(self.address, sizeof(self.type))
        return self.type.from_buffer_copy(value)

    @value.setter
    def value(self, arg) -> None:
        if not isinstance(arg, self.type):
            try:
                arg = self.type(arg)
            except TypeError:
                arg = self.type(*arg)

        value = bytes(arg)
        self._mem_write(self.address, value)

    def __getattribute__(self, key: str) -> Any:
        if key == 'type' or key == 'address' or key == 'value':
            return object.__getattribute__(self, key)

        if not isinstance(self.type, Structure) and not isinstance(self.type, Union):
            return object.__getattribute__(self, key)

        offset = 0
        for name, type in self.type._fields_:
            if name == key:
                return Variable(self.address+offset, type)
            offset += sizeof(type)

        return object.__getattribute__(self, key)


class Function(GeneratorBackend):
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


class FunctionType():
    """Function type for"""

    def __sizeof__(self) -> int:
        return MACHINE_ADDR_SIZE


def PointerClass(size):
    """Factory of pointer classes"""
    class Pointer(ADDR_SIZE_MAP[MACHINE_ADDR_SIZE]):
        pointed_size = size

        def __sizeof__(self) -> int:
            return MACHINE_ADDR_SIZE

    return Pointer


class Enum():
    """Enumerators in program inherit from this class"""

    def __init__(self):
        pass


class Void():
    """Dummy class for void type"""

    def __sizeof__(self) -> int:
        return 0
