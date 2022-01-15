from functools import reduce

from elftools.dwarf.dwarf_expr import DW_OP_name2opcode

from program.exceptions import IncorrectLocationEncodingError


def eval_dwarf_location(location: list[int], endian_little: bool = True) -> int:
    """Counts address of given dwarf location information"""
    if len(location) < 1:
        raise IncorrectLocationEncodingError('Location information is empty')

    addr = 0
    match(location[0]):
        case op if op == DW_OP_name2opcode['DW_OP_addr']:
            encoded_addr = location[-1:0:-1] if endian_little else location[1::]
            addr = reduce(lambda t, s: t*256 + s, encoded_addr, 0)
        case _:
            raise IncorrectLocationEncodingError('Location operation not supported')

    return addr
