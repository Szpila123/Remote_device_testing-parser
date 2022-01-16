from itertools import chain
from pathlib import Path
from program.generator.constants import GENERATED_FILE_IMPORTS

from program.program_abc import ProgramABC
from program.program_function import ProgramFunction
from program.program_type import ProgramType, ProgramTypeBase, ProgramTypeEnum, ProgramTypeTypedef
from program.program_variable import ProgramVariable


class ProgramFile(object):
    """Class instance represents single file which took part in builing of executable."""

    def __init__(self, name: str, types: list[ProgramType], variables: list[ProgramVariable], functions: list[ProgramFunction]) -> None:
        self.name = name
        self.types = types
        self.variables = variables
        self.functions = functions
        self.objects_ref: dict[int, ProgramABC] = dict([(obj.offset, obj)
                                                       for obj in chain(types, variables, functions)])

        for type in self.types:
            print(type)
            type.resolve_refs(self.objects_ref)

    def __str__(self) -> str:
        return f'ProgramFile {self.name}'

    def generate_file(self, path: Path) -> None:
        """Generates code for use with testing framework under given path"""
        code = self.generate_code()

    def generate_code(self) -> str:
        """Returns code inserted to generated file"""
        code = GENERATED_FILE_IMPORTS
        code += self._get_code_types()

        return code

    def _get_code_types(self) -> str:
        """Generate code for program types"""
        code = ''
        done = set(type for type in self.types if type.get_class() is ProgramTypeBase)

        # Generate enums first, as they don't have dependencies
        for type in self.types:
            if type.get_class() is ProgramTypeEnum:
                code += type.generate_code()
                done.add(type)
        code += '\n'

        # Generate the rest of types in given file
        for type in self.types:
            if type not in done and all(map(lambda x: x in done, type.dependencies)):
                code += type.generate_code()
                code += '\n'
                done.add(type)

        return code

    def _get_code_typedefs(self) -> str:
        """Generate code for typedefinitions"""
        code = ''
        for type in self.types:
            if type.get_class is ProgramTypeTypedef:
                code += type.generate_code()

        return code
