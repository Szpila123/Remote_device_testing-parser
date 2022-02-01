#!/usr/bin/python
import backend as backend
import generated.program_c as code

import dbus


class DBUSMemoryAccess(object):
    """Class defines memory access for test framework"""
    X86_64_OFFSET = 0x555555554000
    MESSAGE_SIZE = 64
    OP_CODES = dict(write=1, read=2, execute=3)

    def __init__(self) -> None:
        self.bus = dbus.SessionBus()
        self.object = self.bus.get_object('org.example.Program', '/org/example/Program')
        # print(self.object.Introspect(dbus_interface='org.freedesktop.DBus.Introspectable'))

    def memory_write(self, address: int,  data: bytes) -> None:
        address += self.X86_64_OFFSET
        self.object.Write(address, len(data), data, dbus_interface='org.example.TestsInterface')
        pass

    def memory_read(self, address: int,  size: int) -> bytes:
        address += self.X86_64_OFFSET
        data = self.object.Read(address, size, dbus_interface='org.example.TestsInterface')
        return bytes(data)

    def execute(self, address: int, args: list[bytes], ret_size: int) -> bytes:
        return NotImplemented


def main() -> int:
    """Main procedure of test framework"""
    backend.GeneratorBackend.MemoryAccess = DBUSMemoryAccess()
    program_c = code.Code()
    test_value = bytearray('Test', 'ascii')

    print('Test start:\n')

    # Read and write value in memory

    print('\tRead buffer:', program_c.buffer.value[:])

    print('\tWrite value', test_value)
    program_c.buffer.value = test_value

    print('\tRead buffer:', program_c.buffer.value[:])

    return 0


if __name__ == '__main__':
    exit(main())
