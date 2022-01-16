from typing import Optional

from elftools.dwarf.die import DIE
from elftools.dwarf.dwarf_expr import DW_OP_name2opcode

from elf.constants import ENCODING

from program.utils import eval_dwarf_location
from program.exceptions import LocalVariableError
from program.program_abc import ProgramABC
from program.program_type import ProgramType


class ProgramVariable(ProgramABC):
    """Instances of this class represent variables of the program"""

    def __init__(self, die: DIE) -> None:
        super().__init__(die)
        self.name = str(self.get_die_attribute('DW_AT_name'), ENCODING)

        self.reference = self.get_die_attribute('DW_AT_type')
        self.address = self._get_address()
        self._dependency = None

    def _get_address(self) -> int:
        """Get variable's run-time address"""
        location = self.get_die_attribute('DW_AT_location')
        if not self.get_die_attribute('DW_AT_external') and location[0] != DW_OP_name2opcode['DW_OP_addr']:
            raise LocalVariableError(f'Variable {self.name}, offset {self.offset} is a local variable')

        return eval_dwarf_location(location)

    def __str__(self) -> str:
        description = super().__str__()
        description += f'ProgramVariable {self.name} addr {self.address:#x} ref {self.reference}'
        return description

    def generate_code(self) -> str:
        """Gerenare code with definition of given variable"""
        return f'{self.name} = Variable({self.address:#x}, {self._dependency.alias})\n'

    def resolve_refs(self, obj_refs: dict[int, ProgramABC]) -> None:
        """Resolve type reference of given variable"""
        self._dependency = obj_refs[self.reference]

    @property
    def dependency(self) -> Optional[list[ProgramType]]:
        return [self.dependency] if self._dependency is not None else None
