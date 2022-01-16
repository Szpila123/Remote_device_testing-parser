from enum import Enum

BITS_IN_BYTE = 8

# Mapping of section type to special section name
SECTION_MAP_TYPE: dict[str, str] = {
    'SHT_STRTAB': '.strtab',
    'SHT_SYMTAB': '.symtab',
    'SHT_DYNAMIC': '.dynamic',
    'SHT_NOTE': '.note',
    'SHT_PROGBITS': '.bss',
    'SHT_HASH': '.hash'}

# Tags of type modifiers
DIE_TYPE_MODIFIER_TAGS: tuple[str] = (
    'DW_TAG_pointer_type',
    'DW_TAG_const_type',
    'DW_TAG_volatile_type'
)

# Tags of types that aggregate values
DIE_TYPE_COLLECTION_TAGS: tuple[str] = (
    'DW_TAG_structure_type',
    'DW_TAG_union_type',
)

# Tags of types
DIE_TYPE_TAGS: tuple[str] = (
    'DW_TAG_base_type',
    'DW_TAG_typedef',
    'DW_TAG_array_type',
    'DW_TAG_enumeration_type',
    'DW_TAG_subroutine_type',
    *DIE_TYPE_COLLECTION_TAGS,
    *DIE_TYPE_MODIFIER_TAGS
)

# Tags of functions
DIE_FUNCTION_TAGS: tuple[str] = (
    'DW_TAG_subprogram'
)

# Tags of variables
DIE_VARIABLE_TAGS: tuple[str] = (
    'DW_TAG_variable'
)

REFERENCE_FORM_WITH_OFFSET: tuple[str] = (
    'DW_FORM_ref1',
    'DW_FORM_ref2',
    'DW_FORM_ref4',
    'DW_FORM_ref8',
)


ENCODING = 'utf8'
