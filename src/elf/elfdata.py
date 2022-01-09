import io
import logging
import elftools.elf.elffile as elffile
from elftools.elf.sections import Symbol, SymbolTableSection
from common.exceptions import ParserException
from elf.constants import section_map_type


class MissingDwarfInfoError(ParserException):
    """Exception for missing dwarf comments in elf file"""
    pass


class MissingSymbolTableError(ParserException):
    """Exception for missing symbol table section in elf file"""
    pass


class ELFData(object):
    """Class used for accessing elffile data with high level interface.

    Keyword Arguemnts:
        - file -- executable elf file from which data will be exctracted
    """

    def __init__(self, file_name: str):
        self._file_name = file_name

        # Read file to memory
        with open(self._file_name, 'rb', buffering=0) as file:
            logging.debug(f'Loading file {self._file_name}')
            file_image = io.BytesIO(file.readall())

        # Create elffile class instance
        elf_file = elffile.ELFFile(file_image)
        if not elf_file.has_dwarf_info():
            raise MissingDwarfInfoError(f'{self._file_name} is missing dwarf information')

        # Extract needed information
        self._dwarfinfo = elf_file.get_dwarf_info()
        self._cus = list(self._dwarfinfo.iter_CUs())
        self._symbols = _read_symbols(elf_file)

        # Release file cached in memory
        file_image.close()


def _read_symbols(elffile: elffile.ELFFile) -> list[Symbol]:
    """Read all symbols from symbol table section of elffile"""

    symbol_table: SymbolTableSection = elffile.get_section_by_name(section_map_type['SHT_SYMTAB'])
    if not symbol_table:
        raise MissingSymbolTableError(f'Elffile is missing symbol table section')

    return list(symbol_table.iter_symbols())
