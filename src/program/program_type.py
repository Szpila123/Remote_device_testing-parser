from abc import abstractproperty
from collections import namedtuple
from math import ceil
from typing import Optional

from elftools.dwarf.die import DIE

from common.exceptions import WrongDIEType

from elf.constants import BITS_IN_BYTE, DIE_TYPE_COLLECTION_TAGS, DIE_TYPE_MODIFIER_TAGS, ENCODING, REFERENCE_FORM_WITH_OFFSET

from program.exceptions import ModifierTypeWithNoReferenceError, NonResolvedReferenceError, UnexpectedChildError
from program.program_abc import ProgramABC
from program.generator.constants import size_map, types_map


class ProgramType(ProgramABC):
    """Class represent types of the program

        - dependencies - property retruns list of type dependencies, or None if
        references were not resolved
        - create() - classmethod creates type object for given DIE
        - get_class() - method returns specific class of given type
        - alias - members value is alias of given type in generated code -
         alias is available only after reference resolution
    """

    alias: str

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
            case 'DW_TAG_subroutine_type':
                return ProgramTypeFunction(die)
            case _:
                raise WrongDIEType(f'Creating ProgramType subclass instance with die of tag {die.tag}')

    @abstractproperty
    def dependencies(self) -> Optional[list['ProgramType']]: ...


class ProgramTypeCollection(ProgramType):
    """Class represents all collection datatypes"""
    Member = namedtuple('Member', ['name', 'reference', 'offset', 'bitfield'])
    BitField = namedtuple('Bitfield', ['bitsize', 'bitoffset'])

    def __init__(self, die: DIE) -> None:
        super().__init__(die)
        self.alias: str = str(self.get_die_attribute('DW_AT_name'), ENCODING)
        self.size = self.get_die_attribute('DW_AT_byte_size')
        self.members_refs = self._parse_members()
        self._dependencies = None

    @classmethod
    def create(cle, die: DIE) -> 'ProgramTypeCollection':
        """Creates collection type for given DIE"""
        match(die.tag):
            case 'DW_TAG_structure_type':
                return ProgramTypeStructure(die)
            case 'DW_TAG_union_type':
                return ProgramTypeUnion(die)
            case _:
                raise WrongDIEType(f'Creating ProgramTypeCollection subclass instance with die of tag {die.tag}')

    def resolve_refs(self, object_refs: dict[int, ProgramABC]) -> None:
        """Resolve references for collection members"""
        self._dependencies = [object_refs[ref.reference] for ref in self.members_refs]

    @property
    def dependencies(self) -> list['ProgramType']:
        """Returns dependencies dictated by members or None if
        dependencies not resolved.
        """
        return self._dependencies

    def _parse_members(self) -> list[Member]:
        """Get all structure members, their type references and offsets"""
        members = []
        for child in self.die.iter_children():

            if child.tag != 'DW_TAG_member':
                raise UnexpectedChildError(f'Collection {self.alias} has child of type {child.tag}')

            name = str(child.attributes['DW_AT_name'].value, ENCODING)
            reference = child.attributes['DW_AT_type'].value
            if child.attributes['DW_AT_type'].form in REFERENCE_FORM_WITH_OFFSET:
                reference += self.die.cu.cu_offset

            offset = 0
            if 'DW_AT_data_member_location' in child.attributes:
                offset = child.attributes['DW_AT_data_member_location'].value

            bitfield = None
            if 'DW_AT_bit_size' in child.attributes:
                bitsize = child.attributes['DW_AT_bit_size'].value
                bitoffset = child.attributes['DW_AT_bit_offset'].value
                bitfield = self.BitField(bitsize, bitoffset)

            members.append(self.Member(name, reference, offset, bitfield))

        return members

    def _get_members_str(self) -> str:
        """Retruns string descripting collections's members"""
        description = ''
        for member in self.members_refs:
            description += f'\n\t{member}'
        return description

    def _generate_members(self) -> str:
        """Generate fields of collections members"""
        code = f'\t_fields_ = [\n'

        for member, dep in zip(self.members_refs, self._dependencies):
            code += f'\t\t("{member.name}", {dep.alias}),\n'
        code += f'\t]\n'

        return code


class ProgramTypeModifier(ProgramType):
    """Class represents modifier of program type"""

    def __init__(self, die: DIE):
        super().__init__(die)
        self.alias = None
        self.reference: int = self.get_die_attribute('DW_AT_type')
        self.size: int = self.get_die_attribute('DW_AT_byte_size')
        self._dependency = None

        if self.size is None and self.reference is None:
            raise ModifierTypeWithNoReferenceError(f'DIE offset {self.offset} of {die.tag} has no reference')

    def resolve_refs(self, object_refs: dict[int, ProgramABC]) -> None:
        """Resolve reference of type modifier"""
        if self.reference is not None:
            self._dependency = object_refs[self.reference]
            self.alias = self._dependency.alias
            self.size = self._dependency.size

    @property
    def dependencies(self) -> list['ProgramType']:
        """Dependency of type modifier or None if not resolved.
        In case of void pointer no reference is omitted.
        """
        if self.reference is not None:
            return [self._dependency] if self._dependency is not None else None
        return []

    @classmethod
    def create(cls, die: DIE) -> Optional['ProgramTypeModifier']:
        """Create type modifier for given DIE"""
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
        self.alias = None

    def __str__(self) -> str:
        description = super().__str__()
        return description + f'ProgramTypePointer to size {self.ref_size}'

    def resolve_refs(self, object_refs: dict[int, ProgramABC]) -> None:
        """Resolve reference of type modifier"""
        if self.reference is not None:
            self._dependency = object_refs[self.reference]
            self.refsize = self._dependency.size if self._dependency.size else self.size
        else:
            self.refsize = self.size

        self.alias = f'PointerClass({self.refsize})'

    def generate_code(self) -> str:
        """Generate code for pointer type"""
        return ''

    @property
    def dependencies(self) -> list['ProgramType']:
        """Pointers have no dependencies"""
        return []


class ProgramTypeConst(ProgramTypeModifier):
    """Instances of this class are const modifiers"""

    def __init__(self, die: DIE) -> None:
        super().__init__(die)

    def __str__(self) -> str:
        description = super().__str__()
        return description + f'ProgramTypeConst to {self.reference}'

    def generate_code(self) -> str:
        """Const modifier is omitted."""
        return ''


class ProgramTypeVolatile(ProgramTypeModifier):
    """Instances of this class are volatile modifiers"""

    def __init__(self, die: DIE) -> None:
        super().__init__(die)

    def __str__(self) -> str:
        description = super().__str__()
        return description + f'ProgramTypeVolatile to {self.reference}'

    def generate_code(self) -> str:
        """Volatile modifier is omitted."""
        return ''


class ProgramTypeBase(ProgramType):
    """Instances of this class are base program types"""

    def __init__(self, die: DIE) -> None:
        super().__init__(die)

        self._name = str(self.get_die_attribute('DW_AT_name'), ENCODING)
        self.alias = types_map[self._name]
        self.bitsize = self.get_die_attribute('DW_AT_byte_size') * BITS_IN_BYTE
        if self.bitsize is None:
            self.bitsize = self.get_die_attribute('DW_AT_bit_size')
            self.bitoffset = self.get_die_attribute('DW_AT_bit_offset')

    @property
    def size(self) -> int:
        """Size of a type in bytes"""
        return ceil(self.bitsize / BITS_IN_BYTE)

    @property
    def dependencies(self) -> Optional[list['ProgramType']]:
        """Base types have no dependencies, returns empty list"""
        return []

    def resolve_refs(self, object_refs: dict[int, ProgramABC]) -> None:
        """Base types have no references"""
        return

    def __str__(self) -> str:
        description = super().__str__()
        return description + f'Base type {self.alias} of size {self.size}'

    def generate_code(self) -> str:
        """Returns ctype type for given base type"""
        return self.alias


class ProgramTypeEnum(ProgramType):
    """Instances of this class are enumeration types"""
    Enumerator = namedtuple('Enumerator', ['name', 'value'])

    def __init__(self, die: DIE) -> None:
        super().__init__(die)
        self.alias: str = str(self.get_die_attribute('DW_AT_name'), ENCODING)
        self.size: int = self.get_die_attribute('DW_AT_byte_size')
        self.enumerators = self._parse_enumerators()

    def __str__(self) -> str:
        description = super().__str__()
        description += f'ProgramTypeEnum {self.alias}'
        description += self._get_enumerators_str()
        return description

    @property
    def dependencies(self) -> Optional[list['ProgramType']]:
        """Enumerators have no dependencies, returns empty list"""
        return []

    def resolve_refs(self, object_refs: dict[int, ProgramABC]) -> None:
        """Enumerators have no references"""
        return

    def generate_code(self) -> str:
        """Generate code of enumeration class"""
        code = f'class {self.alias}({size_map[self.size]}, Enum):\n'
        code += f'\t_type = {size_map[self.size]}\n'

        for enumerator in self.enumerators:
            code += f'\t{enumerator.name} = {enumerator.value}\n'

        return code

    def _parse_enumerators(self) -> list[Enumerator]:
        """Get all structure members, their type references and offsets"""
        enumerators = []
        for child in self.die.iter_children():
            if child.tag != 'DW_TAG_enumerator':
                raise UnexpectedChildError(f'Enumerators {self.alias} has child of type {child.tag}')

            name = str(child.attributes['DW_AT_name'].value, ENCODING)
            value = child.attributes['DW_AT_const_value'].value

            enumerators.append(self.Enumerator(name, value))

        return enumerators

    def _get_enumerators_str(self) -> str:
        """Retruns string descripting it's members"""
        description = ''
        for member in self.enumerators:
            description += f'\n\t{member}'
        return description


class ProgramTypeUnion(ProgramTypeCollection):
    """Instances of this class are union types"""

    def __str__(self) -> str:
        description = super().__str__()
        description += f'ProgramTypeUnion {self.alias}'
        description += self._get_members_str()
        return description

    def generate_code(self) -> str:
        """Generate code of ctype Union class"""
        code = f'class {self.alias}(Union):\n'
        code += self._generate_members()
        return code


class ProgramTypeTypedef(ProgramType):
    """Instances of this class are type definitions"""

    def __init__(self, die: DIE) -> None:
        super().__init__(die)
        self.alias: str = str(self.get_die_attribute('DW_AT_name'), ENCODING)
        self.reference: int = self.get_die_attribute('DW_AT_type')
        self.size: int = self.get_die_attribute('DW_AT_size')
        self._dependency: Optional[ProgramType] = None

    def __str__(self) -> str:
        description = super().__str__()
        return description + f'ProgramTypeTypedef of {self.alias} to reference {self.reference or "Void"}'

    def resolve_refs(self, object_refs: dict[int, ProgramABC]) -> None:
        """Resolve reference for given type alias"""
        if self.reference is None:
            self._dependency = []
        else:
            self._dependency = [object_refs[self.reference]]

    @property
    def dependencies(self) -> Optional[list['ProgramType']]:
        """Return dependencies or none if dependencies to resolved """
        return self._dependency

    def generate_code(self) -> str:
        """Generate type alias for given name"""
        if self._dependency is None:
            raise NonResolvedReferenceError(f'{self.alias} generates code with unresolved reference')

        if self._dependency == []:
            code = f'{self.alias} = Void\n'
        else:
            code = f'{self.alias} = {self._dependency[0].alias}\n'
        return code


class ProgramTypeStructure(ProgramTypeCollection):
    """Instances of this class are structure types"""

    def __str__(self) -> str:
        description = super().__str__()
        description += f'ProgramTypeStructure {self.alias}'
        description += self._get_members_str()
        return description

    def generate_code(self) -> str:
        """Generates code of structure type"""
        code = f'class {self.alias}(Structure):\n'
        code += self._generate_members()
        return code


class ProgramTypeArray(ProgramType):
    """Instances of this class are array types"""

    def __init__(self, die: DIE) -> None:
        super().__init__(die)
        self.reference = self.get_die_attribute('DW_AT_type')
        self.alias = None
        self._dependency = None
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

    @property
    def dependencies(self) -> Optional[list['ProgramType']]:
        """Return array type dependency or None if dependency not resolved"""
        return [self._dependency] if self._dependency is not None else None

    def resolve_refs(self, object_refs: dict[int, ProgramABC]) -> None:
        """Resolve array type dependency"""
        self._dependency = object_refs[self.reference]
        self.alias = f'{self._dependency.alias}_array'

    def generate_code(self) -> str:
        """Generate definition of given array type"""
        return f'{self.alias} = {self._dependency.alias} * {self.count}'


class ProgramTypeFunction(ProgramType):
    ArgumentType = namedtuple('ArgumentType', ['reference'])

    def __init__(self, die: DIE):
        super().__init__(die)
        self.reference: int = self.get_die_attribute('DW_AT_type')
        self.arg_types: list[self.ArgumentType] = self._parse_arguments()
        self.size: int = self.get_die_attribute('DW_AT_byte_size')
        self._dependency = None
        self.alias = None

    def __str__(self) -> str:
        description = super().__str__()
        description += f'ProgramTypeFunction of reference {self.reference}'
        description += self._get_arguments_str()
        return description

    @property
    def dependencies(self) -> Optional[list['ProgramType']]:
        """Dependencies of given function type, None if dependencies were not resolved"""
        return self._dependency

    def resolve_refs(self, object_refs: dict[int, ProgramABC]) -> None:
        """Resolve dependencies of given funciton type"""
        self._dependency = []
        if self.reference:
            self._dependency += [object_refs[self.reference]]
        self._dependency += [object_refs[arg.reference] for arg in self.arg_types]
        self.alias = f'FunctionType_{self.offset}'

    def generate_code(self) -> str:
        """Generate code of given function - create function type class"""
        code = f'class {self.alias}(FunctionType):\n'
        code += f'\t_return_type = {self._dependency[0].alias if self.reference else "Void"}\n'
        code += f'\t_args = [{", ".join(arg.alias for arg in self._dependency[1:])}]\n'

        return code

    def _parse_arguments(self) -> list[ArgumentType]:
        """Get all function type argument types references"""
        arg_types = []
        for child in self.die.iter_children():
            if child.tag != 'DW_TAG_formal_parameter':
                raise UnexpectedChildError(f'Function type of offset {self.offset} has child of type {child.tag}')

            reference = child.attributes['DW_AT_type'].value
            if child.attributes['DW_AT_type'].form in REFERENCE_FORM_WITH_OFFSET:
                reference += self.die.cu.cu_offset

            arg_types.append(self.ArgumentType(reference))

        return arg_types

    def _get_arguments_str(self) -> str:
        """Retruns string descripting it's members"""
        description = ''
        for arg_type in self.arg_types:
            description += f'\n\t{arg_type}'
        return description
