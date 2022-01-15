from program.program_function import ProgramFunction
from program.program_type import ProgramType
from program.program_variable import ProgramVariable


class ProgramFile(object):
    """Class instance represents single file which took part in builing of executable."""

    def __init__(self, types: list[ProgramType], variables: list[ProgramVariable], functions: list[ProgramFunction]) -> None:
        pass

    def __str__(self) -> str:
        pass
