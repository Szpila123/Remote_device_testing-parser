from abc import ABC, abstractmethod, abstractstaticmethod


class ProgramABC(ABC):
    """Abstract class for all Program objects classes"""

    @abstractmethod
    def __init__() -> None: ...

    @abstractmethod
    def __str__(self) -> str: ...
