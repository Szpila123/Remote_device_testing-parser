from itertools import chain
from pathlib import Path
from common.exceptions import FileWriteError
from program.generator.constants import GENERATED_FILE_IMPORTS

from program.program_abc import ProgramABC
from program.program_function import ProgramFunction
from program.program_type import ProgramType, ProgramTypeBase, ProgramTypeEnum, ProgramTypeTypedef
from program.program_variable import ProgramVariable


class ProgramFile(object):
    """Class instance represents single file which took part in builing of executable."""

    def __init__(self, name: str, types: list[ProgramType], variables: list[ProgramVariable], functions: list[ProgramFunction]) -> None:
        self.name = name
        self.filename = f'{self.name.replace(".", "_")}.py'
        self.types = types
        self.variables = variables
        self.functions = functions
        self.objects_ref: dict[int, ProgramABC] = dict([(obj.offset, obj)
                                                       for obj in chain(types, variables, functions)])

        for obj in chain(self.types, self.variables, self.functions):
            obj.resolve_refs(self.objects_ref)

    def __str__(self) -> str:
        return f'ProgramFile {self.name}'

    def generate_file(self, path: Path) -> None:
        """Generates code for use with testing framework under given path"""
        code = self.generate_code()
        with open(path / self.filename, 'w') as file:
            written = file.write(code)
            if written < len(code):
                raise FileWriteError(f'{self.filename}: write did not store all specified data')

    def generate_code(self) -> str:
        """Returns code inserted to generated file"""
        code = GENERATED_FILE_IMPORTS
        code += self._get_code_types()
        code += 'class Code(object):\n'
        code += '\tdef __init__(self):\n'
        code += '\t\t' + '\t\t'.join(self._get_code_variables().splitlines(keepends=True))
        code += '\n'
        code += '\t\t' + '\t\t'.join(self._get_code_functions().splitlines(keepends=True))

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
        while len(self.types) != len(done):
            for type in self.types:
                if type not in done and all(map(lambda x: x in done, type.dependencies)):
                    code += type.generate_code()
                    code += '\n'
                    done.add(type)

        return code

    def _get_code_variables(self) -> str:
        """Generate code for program variables"""
        return ''.join(f'self.{var.generate_code()}' for var in self.variables)

    def _get_code_functions(self) -> str:
        """Generate code for program functions"""
        return ''.join(f'self.{func.generate_code()}' for func in self.functions)
