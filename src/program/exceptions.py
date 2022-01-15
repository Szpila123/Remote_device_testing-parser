from common.exceptions import ParserException


class ModifierTypeWithNoReferenceError(ParserException):
    """Error raised when creating modifier type that has no reference to another DIE"""
    pass


class UnexpectedChildError(ParserException):
    """Error raised when DIE has unknown child"""
    pass
