import io
import logging
import itertools
from typing import Optional

import elftools.elf.elffile as elffile
from elftools.elf.sections import Symbol, SymbolTableSection
from elftools.dwarf.compileunit import CompileUnit

from common.exceptions import ParserException, WrongArgumentValueError
from elf.constants import section_map_type

from program.program_file import ProgramFile
from program.program_type import ProgramType
from program.program_function import ProgramFunction
from program.program_variable import ProgramVariable


class MissingDwarfInfoError(ParserException):
    """Exception for missing dwarf comments in elf file"""
    pass


class MissingSymbolTableError(ParserException):
    """Exception for missing symbol table section in elf file"""
    pass


class FilenameNotFoundError(ParserException):
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

        # Collect all filenames from which elf was built,
        self._files: dict[str, Optional[CompileUnit]] = dict(
            zip([symbol.name for symbol in self._symbols if symbol.name.endswith('.c')], itertools.repeat(None)))

        # Assign cus to their files
        for cu in self._cus:
            file_name = str(cu.get_top_DIE().attributes['DW_AT_name'].value, 'utf8')
            self._files[file_name] = cu

        self.get_files_data()

    @property
    def file_names(self) -> list[str]:
        """Get list of all file names that were used during compilation of program"""
        return self._files.keys()

    def get_files_data(self) -> list[ProgramFile]:
        """Eject information about separate files from elf data"""
        for file_name, cu in self._files.items():
            if cu is None:
                continue
            file_types = self.get_types(file_name)
            file_variables = self.get_variables(file_name)
            file_funcitons = self.get_functions(file_name)

    def get_types(self, file_name: str) -> list[ProgramType]:
        """Get all types defined in a given file"""
        if not self._file_has_cu(file_name):
            return []

        top_die = self._files[file_name].get_top_DIE()

    def get_variables(self, file_name: str) -> list[ProgramVariable]:
        """Get all variables defined in a given file"""
        if not self._file_has_cu(file_name):
            return []

        top_die = self._files[file_name].get_top_DIE()

    def get_functions(self, file_name: str) -> list[ProgramFunction]:
        """Get all functions defined in a given file"""
        if not self._file_has_cu(file_name):
            return []

        top_die = self._files[file_name].get_top_DIE()

    def _file_has_cu(self, file_name: str) -> bool:
        """Check if given file has it's cu"""
        if file_name not in self._files:
            raise WrongArgumentValueError('File name not found')

        return self._files[file_name] is not None


def _read_symbols(elffile: elffile.ELFFile) -> list[Symbol]:
    """Read all symbols from symbol table section of elffile"""

    symbol_table: SymbolTableSection = elffile.get_section_by_name(section_map_type['SHT_SYMTAB'])
    if not symbol_table:
        raise MissingSymbolTableError(f'Elffile is missing symbol table section')

    return list(symbol_table.iter_symbols())
