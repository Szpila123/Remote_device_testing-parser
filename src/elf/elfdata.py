import io
import logging
import itertools
from typing import Optional
from elftools.dwarf.die import DIE

import elftools.elf.elffile as elffile
from elftools.dwarf.compileunit import CompileUnit

from elf.exceptions import MissingDwarfInfoError
from elf.utils import get_die_type, read_ELF_symbol_section


from program.program_file import ProgramFile
from program.program_type import ProgramType
from program.program_function import ProgramFunction
from program.program_variable import ProgramVariable
from program.exceptions import FuncitonAddressMissingError, LocalVariableError


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
        self._symbols = read_ELF_symbol_section(elf_file)

        # Release file cached in memory
        file_image.close()

        # Collect all filenames from which elf was built,
        self._files: dict[str, Optional[CompileUnit]] = dict(
            zip([symbol.name for symbol in self._symbols if symbol.name.endswith('.c')], itertools.repeat(None)))

        # Assign cus to their files
        for cu in self._cus:
            file_name = str(cu.get_top_DIE().attributes['DW_AT_name'].value, 'utf8')
            self._files[file_name] = cu

    @property
    def file_names(self) -> list[str]:
        """List of all file names that were used during compilation of a program."""
        return self._files.keys()

    def parse_elffile(self) -> list[ProgramFile]:
        """Eject information about separate files from elf data."""
        parsed_files = []
        for file_name, cu in self._files.items():
            if cu is None:
                continue
            logging.debug(f'Parsing file {file_name}')

            # Sort die's by object which they represent
            cu_objects = self._get_cu_objects(cu)

            # Create coresponding object representations
            file_types = self._create_types(cu_objects[ProgramType])
            file_variables = self._create_variables(cu_objects[ProgramVariable])
            file_functions = self._create_functions(cu_objects[ProgramFunction])

            for object in itertools.chain(file_types, file_variables, file_functions):
                logging.info(object)

            # Create representations of object file/cu
            parsed_files.append(ProgramFile(file_name, file_types, file_variables, file_functions))

        return parsed_files

    def _create_types(self, type_dies: list[DIE]) -> list[ProgramType]:
        """Get all types defined in a given file."""
        return list(filter(None, (ProgramType.create(die) for die in type_dies)))

    def _create_variables(self, variable_dies: list[DIE]) -> list[ProgramVariable]:
        """Get all variables defined in a given file."""
        variables = []
        for var_die in variable_dies:
            try:
                variables.append(ProgramVariable(var_die))
            except LocalVariableError:
                logging.debug(f'Variables: skipping {var_die}')

        return variables

    def _create_functions(self, function_dies: list[DIE]) -> list[ProgramFunction]:
        """Get all functions defined in a given file."""
        functions = []
        for func_die in function_dies:
            try:
                functions.append(ProgramFunction(func_die))
            except FuncitonAddressMissingError:
                logging.debug(f'Functions: skipping {func_die}')

        return functions

    def _get_cu_objects(self, cu: CompileUnit) -> dict[str, list[DIE]]:
        """Segregates die's in compilation unit by object which dies represent."""
        objects = {ProgramFunction: [], ProgramVariable: [], ProgramType: []}
        for die in cu.iter_DIEs():
            if die.is_null():
                continue

            try:
                objects[get_die_type(die)].append(die)
            except KeyError:
                logging.warning(f'DIE with offset {die.offset} does not have corresponding program object')
                logging.debug(f'DIE: {die}')

        return objects
