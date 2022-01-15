from collections import namedtuple

from elftools.dwarf.die import DIE

from program.exceptions import UnexpectedChildError
from program.program_abc import ProgramABC


class ProgramFunction(ProgramABC):
    """Instances of this class represent functions of the program"""
    Argument = namedtuple('Argument', ['name', 'ref'])

    def __init__(self, die: DIE) -> None:
        super().__init__(die)
        self.name = self.get_die_attribute('DW_AT_name')
        self.ref = self.get_die_attribute('DW_AT_type')
        self.args = self._parse_args()
        self.address = self.get_die_attribute('DW_AT_low_pc')

    def __str__(self) -> str:
        description = super().__str__()
        description += f'ProgramFunction {self.name} ref {self.ref} addr {self.address:#x}'
        description += self._get_args_str()
        return description

    def _parse_args(self) -> list[Argument]:
        """Get all function arguments and their types"""
        args = []
        for child in self.die.iter_children():
            match(child.tag):
                case 'DW_TAG_formal_parameter':
                    name = child.attributes['DW_AT_name'].value if 'DW_AT_name' in child.attributes else ''
                    reference = child.attributes['DW_AT_type'].value
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
