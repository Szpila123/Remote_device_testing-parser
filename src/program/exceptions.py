from common.exceptions import ParserException


class ModifierTypeWithNoReferenceError(ParserException):
    """Error raised when creating modifier type that has no reference to another DIE"""
    pass


class UnexpectedChildError(ParserException):
    """Error raised when DIE has unknown child"""
    pass


class LocalVariableError(ParserException):
    """Error raised when DIE represents non-external variable"""
    pass


class IncorrectLocationEncodingError(ParserException):
    """Error raised for location information that has incorrect format"""
    pass


class FuncitonAddressMissingError(ParserException):
    """Error raised when function does not have an address (eg. is external for cu)"""
    pass
