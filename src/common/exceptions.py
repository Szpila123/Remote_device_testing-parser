class ParserException(Exception):
    """Base exception in parser"""
    pass


class WrongArgumentValueError(ParserException):
    """Exception raised for not expected argument values"""
    pass
