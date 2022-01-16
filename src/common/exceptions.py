class ParserException(Exception):
    """Base exception in parser"""
    pass


class WrongArgumentValueError(ParserException):
    """Exception raised for not expected argument values"""
    pass


class WrongDIEType(ParserException):
    """Exception raised when DIE is used to to create wrong object"""
    pass


class FileWriteError(ParserException):
    """Exception raised when data written to file is less then specified"""
    pass
