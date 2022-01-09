# Mapping of section type to special section name
section_map_type: dict[str, str] = {
    'SHT_STRTAB': '.strtab',
    'SHT_SYMTAB': '.symtab',
    'SHT_DYNAMIC': '.dynamic',
    'SHT_NOTE': '.note',
    'SHT_PROGBITS': '.bss',
    'SHT_HASH': '.hash'}
