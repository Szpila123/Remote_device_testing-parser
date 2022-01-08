import io
import logging
import elftools.elf.elffile as elffile
from common.exceptions import ParserException


class MissingDwarfInfoError(ParserException):
    """Exception for missing dwarf comments in elf file"""
    pass


def load_elffile(file: io.FileIO) -> elffile.ELFFile:
    """Create ELF view of given file"""

    logging.debug(f'Loading file {file.name}')
    efile = elffile.ELFFile(file)

    if not efile.has_dwarf_info:
        raise MissingDwarfInfoError(f'{file.name} is missing dwarf information')