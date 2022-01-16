from collections import namedtuple

from elftools.dwarf.die import DIE
from elf.constants import ENCODING, REFERENCE_FORM_WITH_OFFSET

from program.program_abc import ProgramABC
from program.exceptions import FuncitonAddressMissingError, UnexpectedChildError


class ProgramFunction(ProgramABC):
    """Instances of this class represent functions of the program"""
    Argument = namedtuple('Argument', ['name', 'reference'])

    def __init__(self, die: DIE) -> None:
        super().__init__(die)
        self.name = str(self.get_die_attribute('DW_AT_name'), ENCODING)
        self.reference = self.get_die_attribute('DW_AT_type')
        self.args = self._parse_args()
        self.address = self.get_die_attribute('DW_AT_low_pc')
        self._dependencies = None

        if self.address is None:
            raise FuncitonAddressMissingError(f'Function {self.name} is external to cu of given DIE')

    def __str__(self) -> str:
        description = super().__str__()
        description += f'ProgramFunction {self.name} ref {self.reference} addr {self.address}'
        description += self._get_args_str()
        return description

    def resolve_refs(self, obj_refs: dict[int, ProgramABC]) -> None:
        """Resolve type reference of given function"""
        self._dependencies = [obj_refs[self.reference]] + [obj_refs[arg.reference] for arg in self.args]
        return

    def generate_code(self) -> str:
        """Gerenare code with definition of given function"""
        code = f'{self.name} = Function({self.address:#x},'
        code += f' [{", ".join(obj.alias for obj in self._dependencies[1:])}],'
        code += f' {self._dependencies[0].alias})\n'
        return code

    def _parse_args(self) -> list[Argument]:
        """Get all function arguments and their types"""
        args = []
        for child in self.die.iter_children():
            match(child.tag):
                case 'DW_TAG_formal_parameter':
                    name = child.attributes['DW_AT_name'].value if 'DW_AT_name' in child.attributes else ''
                    reference = child.attributes['DW_AT_type'].value
                    if child.attributes['DW_AT_type'].form in REFERENCE_FORM_WITH_OFFSET:
                        reference += self.die.cu.cu_offset
                    args.append(self.Argument(name, reference))

                case 'DW_TAG_unspecified_parameters':
                    args.append(self.Argument(None, None))

                case 'DW_TAG_variable':
                    continue

                case _:
                    raise UnexpectedChildError(f'Function {self.name} has child of type {child.tag}')

        return args

    def _get_args_str(self) -> str:
        """Retruns string descripting function's arguments"""
        description = ''
        for arg in self.args:
            description += f'\n\t{arg}'
        return description
