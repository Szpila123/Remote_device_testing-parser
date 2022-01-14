from typing import Optional

import elftools.elf.elffile as elffile
from elftools.elf.sections import SymbolTableSection, Symbol
from elftools.dwarf.die import DIE

from elf.constants import DIE_FUNCTION_TAGS, DIE_TYPE_TAGS, DIE_VARIABLE_TAGS, SECTION_MAP_TYPE
from elf.exceptions import MissingSymbolTableError

from program.program_abc import ProgramABC
from program.program_function import ProgramFunction
from program.program_type import ProgramType
from program.program_variable import ProgramVariable


def read_ELF_symbol_section(elffile: elffile.ELFFile) -> list[Symbol]:
    """Read all symbols from symbol table section of elffile"""

    symbol_table: SymbolTableSection = elffile.get_section_by_name(SECTION_MAP_TYPE['SHT_SYMTAB'])
    if not symbol_table:
        raise MissingSymbolTableError(f'Elffile is missing symbol table section')

    return list(symbol_table.iter_symbols())


def get_die_type(die: DIE) -> Optional[ProgramABC]:
    """Return Program type which DIE corespondes to"""

    match(die.tag):
        case x if x in DIE_TYPE_TAGS:
            return ProgramType
        case x if x in DIE_FUNCTION_TAGS:
            return ProgramFunction
        case x if x in DIE_VARIABLE_TAGS:
            return ProgramVariable
        case _:
            return None
