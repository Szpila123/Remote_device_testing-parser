import unittest
from elf.elfdata import ELFData, MissingDwarfInfoError


class TestElfLoader(unittest.TestCase):
    """Test cases for loading of elf file"""

    def test_dwarf_info_missing(self):
        """Checks if program detects lack of dwarf comments"""
        MISSING_DWARF_INFO_FILE = 'tests/testfiles/test_no_dwarf.elf'
        self.assertRaises(MissingDwarfInfoError, ELFData, MISSING_DWARF_INFO_FILE)
