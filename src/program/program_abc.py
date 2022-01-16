from abc import ABC, abstractmethod
from typing import Any

from elftools.dwarf.die import DIE

from elf.constants import REFERENCE_FORM_WITH_OFFSET


class ProgramABC(ABC):
    """Abstract class for all Program objects classes"""
    die: DIE
    offset: int

    def __init__(self, die: DIE) -> None:
        self.die = die
        self.offset = die.offset

    def __str__(self) -> str:
        return f'Offset: {self.offset}\n\t'

    def get_die_attribute(self, attr: str) -> Any:
        """Wrapper for die attributes.
        Check object's DIE for given attribute, return None if missing."""
        value = None
        try:
            value = self.die.attributes[attr].value
        except KeyError:
            return None

        if attr == 'DW_AT_type' and self.die.attributes[attr].form in REFERENCE_FORM_WITH_OFFSET:
            value += self.die.cu.cu_offset

        return value

    @abstractmethod
    def generate_code(self) -> str: ...

    @abstractmethod
    def resolve_refs(self, object_refs: dict[int, 'ProgramABC']) -> None: ...
