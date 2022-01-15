from abc import ABC, abstractmethod, abstractstaticmethod
from typing import Any

from elftools.dwarf.die import DIE


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
        """Check object's DIE for given attribute, return None if missing"""
        try:
            return self.die.attributes[attr].value
        except KeyError:
            return None
