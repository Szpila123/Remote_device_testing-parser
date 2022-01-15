from elftools.dwarf.die import DIE

from program.utils import eval_dwarf_location
from program.exceptions import LocalVariableError
from program.program_abc import ProgramABC


class ProgramVariable(ProgramABC):
    """Instances of this class represent variables of the program"""

    def __init__(self, die: DIE) -> None:
        super().__init__(die)
        self.name = self.get_die_attribute('DW_AT_name')

        if not self.get_die_attribute('DW_AT_external'):
            raise LocalVariableError(f'Variable {self.name}, offset {self.offset} is a local variable')

        self.reference = self.get_die_attribute('DW_AT_type')
        self.address = self._get_address()

    def _get_address(self) -> int:
        """Get variable's run-time address"""
        location = self.get_die_attribute('DW_AT_location')
        return eval_dwarf_location(location)

    def __str__(self) -> str:
        description = super().__str__()
        description += f'ProgramVariable {self.name} addr {self.address:#x} ref {self.reference}'
        return description
