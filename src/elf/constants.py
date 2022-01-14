from enum import Enum


# Mapping of section type to special section name
SECTION_MAP_TYPE: dict[str, str] = {
    'SHT_STRTAB': '.strtab',
    'SHT_SYMTAB': '.symtab',
    'SHT_DYNAMIC': '.dynamic',
    'SHT_NOTE': '.note',
    'SHT_PROGBITS': '.bss',
    'SHT_HASH': '.hash'}

DIE_TYPE_TAGS: tuple[str] = (
    'DW_TAG_strucutre_type',
    'DW_TAG_union_type',
    'DW_TAG_pointer_type',
    'DW_TAG_base_type',
    'DW_TAG_typedef',
    'DW_TAG_const_type',
    'DW_TAG_enumeration_type'
    'DW_TAG_array_type'
)

DIE_FUNCTION_TAGS: tuple[str] = (
    'DW_TAG_subprogram'
)

DIE_VARIABLE_TAGS: tuple[str] = (
    'DW_TAG_variable'
)
