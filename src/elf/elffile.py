import io
import elftools.elf.elffile as elffile
from common.exceptions import ParserException


class MissingDwarfInfoError(ParserException):
    """Exception for missing dwarf comments in elf file"""
    pass


def load_elffile(file: io.FileIO) -> elffile.ELFFile:
    efile = elffile.ELFFile(file)
    if not efile.has_dwarf_info:
        raise MissingDwarfInfoError(f'{file.name} is missing dwarf information')
