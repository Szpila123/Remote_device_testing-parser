from abc import abstractmethod
from collections import namedtuple
from math import ceil
from typing import Any, Optional
from common.exceptions import WrongDIEType
from elf.constants import BITS_IN_BYTE, DIE_TYPE_COLLECTION_TAGS, DIE_TYPE_MODIFIER_TAGS
from program.exceptions import ModifierTypeWithNoReferenceError, UnexpectedChildError
from program.program_abc import ProgramABC

from elftools.dwarf.die import DIE


class ProgramType(ProgramABC):
    """Class represent types of the program"""
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

    @classmethod
    def create(cls, die: DIE) -> Optional['ProgramType']:
        """Create instance of subclass of ProgramType appropriate to given die"""
        match(die.tag):
            case x if x in DIE_TYPE_MODIFIER_TAGS:
                return ProgramTypeModifier.create(die)
            case x if x in DIE_TYPE_COLLECTION_TAGS:
                return ProgramTypeCollection.create(die)
            case 'DW_TAG_enumeration_type':
                return ProgramTypeEnum(die)
            case 'DW_TAG_base_type':
                return ProgramTypeBase(die)
            case 'DW_TAG_typedef':
                return ProgramTypeTypedef(die)
            case 'DW_TAG_array_type':
                return ProgramTypeArray(die)
            case _:
                raise WrongDIEType(f'Creating ProgramType subclass instance with die of tag {die.tag}')

    # TODO: uncomment when ready
    # @abstractmethod
    # def to_code(self) -> str: ...


class ProgramTypeCollection(ProgramType):
    """Class represents all collection datatypes"""
    Member = namedtuple('Member', ['name', 'reference', 'offset'])

    def __init__(self, die: DIE) -> None:
        super().__init__(die)
        self.members_refs = self.parse_members()

    @classmethod
    def create(cle, die: DIE) -> 'ProgramTypeCollection':
        match(die.tag):
            case 'DW_TAG_structure_type':
                return ProgramTypeStructure(die)
            case 'DW_TAG_union_type':
                return ProgramTypeUnion(die)
            case _:
                raise WrongDIEType(f'Creating ProgramTypeCollection subclass instance with die of tag {die.tag}')

    def parse_members(self) -> dict[str, Member]:
        """Get all structure members, their type references and offsets"""
        members = {}
        for child in self.die.iter_children():

            if child.tag != 'DW_TAG_member':
                raise UnexpectedChildError(f'Struct {self.name} has child of type {child.tag}')

            name = child.attributes['DW_AT_name'].value
            reference = child.attributes['DW_AT_type'].value
            offset = 0

            if 'DW_AT_data_member_location' in child.attributes:
                offset = child.attributes['DW_AT_data_member_location'].value

            members[name] = self.Member(name, reference, offset)

        return members

    def _get_member_str(self) -> str:
        """Retruns string descripting it's members"""
        description = ''
        for member in self.members_refs.values():
            description += f'\n\t{member}'
        return description


class ProgramTypeModifier(ProgramType):
    """Class represents modifier of program type"""

    def __init__(self, die: DIE):
        super().__init__(die)
        self.reference: int = self.get_die_attribute('DW_AT_type')
        if self.reference is None:
            raise ModifierTypeWithNoReferenceError(f'DIE offset {self.offset} of {die.tag} has no reference')

    @classmethod
    def create(cls, die: DIE) -> Optional['ProgramTypeModifier']:
        try:
            match(die.tag):
                case 'DW_TAG_pointer_type':
                    return ProgramTypePointer(die)
                case 'DW_TAG_const_type':
                    return ProgramTypeConst(die)
                case 'DW_TAG_volatile_type':
                    return ProgramTypeVolatile(die)
                case _:
                    raise WrongDIEType(f'Creating ProgramTypeModifier subclass instance with die of tag {die.tag}')
        except ModifierTypeWithNoReferenceError:
            return None


class ProgramTypePointer(ProgramTypeModifier):
    """Instances of this class are pointer modifiers"""

    def __init__(self, die: DIE) -> None:
        super().__init__(die)
        self.string = '*'

    def __str__(self) -> str:
        description = super().__str__()
        return description + f'ProgramTypePointer to {self.reference}'


class ProgramTypeConst(ProgramTypeModifier):
    """Instances of this class are const modifiers"""

    def __init__(self, die: DIE) -> None:
        super().__init__(die)
        self.string = ''

    def __str__(self) -> str:
        description = super().__str__()
        return description + f'ProgramTypeConst to {self.reference}'


class ProgramTypeVolatile(ProgramTypeModifier):
    """Instances of this class are volatile modifiers"""

    def __init__(self, die: DIE) -> None:
        super().__init__(die)
        self.string = ''

    def __str__(self) -> str:
        description = super().__str__()
        return description + f'ProgramTypeVolatile to {self.reference}'


class ProgramTypeBase(ProgramType):
    """Instances of this class are base program types"""

    def __init__(self, die: DIE) -> None:
        super().__init__(die)

        self.name = self.get_die_attribute('DW_AT_name')
        self.bitsize = self.get_die_attribute('DW_AT_byte_size') * BITS_IN_BYTE
        if self.bitsize is None:
            self.bitsize = self.get_die_attribute('DW_AT_bit_size')
            self.bitoffset = self.get_die_attribute('DW_AT_bit_offset')

    @property
    def size(self) -> int:
        """Size of a type in bytes"""
        return ceil(self.bitsize / BITS_IN_BYTE)

    def __str__(self) -> str:
        description = super().__str__()
        return description + f'Base type {self.name} of size {self.size}'


class ProgramTypeEnum(ProgramType):
    """Instances of this class are enumeration types"""
    Enumerator = namedtuple('Enumerator', ['name', 'value'])

    def __init__(self, die: DIE) -> None:
        super().__init__(die)

    def __str__(self) -> str:
        description = super().__str__()
        return description + f'ProgramTypeEnum'


class ProgramTypeUnion(ProgramTypeCollection):
    """Instances of this class are union types"""

    def __init__(self, die: DIE) -> None:
        super().__init__(die)

    def __str__(self) -> str:
        description = super().__str__()
        description += f'ProgramTypeUnion'
        description += self._get_member_str()
        return description


class ProgramTypeTypedef(ProgramType):
    """Instances of this class are type definitions"""

    def __init__(self, die: DIE) -> None:
        super().__init__(die)
        self.name = self.get_die_attribute('DW_AT_name')
        self.reference = self.get_die_attribute('DW_AT_type')

    def __str__(self) -> str:
        description = super().__str__()
        return description + f'ProgramTypeTypedef of {self.name} to reference {self.reference}'


class ProgramTypeStructure(ProgramTypeCollection):
    """Instances of this class are structure types"""

    def __init__(self, die: DIE) -> None:
        super().__init__(die)
        self.name = self.get_die_attribute('DW_AT_name')

    def __str__(self) -> str:
        description = super().__str__()
        description += f'ProgramTypeStructure {self.name}'
        description += self._get_member_str()
        return description


class ProgramTypeArray(ProgramType):
    """Instances of this class are array types"""

    def __init__(self, die: DIE) -> None:
        super().__init__(die)
        self.reference = self.get_die_attribute('DW_AT_type')
        for child in self.die.iter_children():
            match(child.tag):
                case 'DW_TAG_subrange_type' if 'DW_AT_upper_bound' in child.attributes:
                    self.count = child.attributes['DW_AT_upper_bound'].value + 1
                    break
                case 'DW_TAG_subrange_type' if 'DW_AT_count' in child.attributes:
                    self.count = child.attributes['DW_AT_count'].value
                    break

    def __str__(self) -> str:
        description = super().__str__()
        return description + f'ProgramTypeArray of reference {self.reference}, elems {self.count}'
