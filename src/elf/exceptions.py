from common.exceptions import ParserException


class MissingDwarfInfoError(ParserException):
    """Exception for missing dwarf comments in elf file"""
    pass


class MissingSymbolTableError(ParserException):
    """Exception for missing symbol table section in elf file"""
    pass


class FilenameNotFoundError(ParserException):
    """Exception for missing symbol table section in elf file"""
    pass
