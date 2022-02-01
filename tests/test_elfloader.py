import unittest
from elf.elfdata import ELFData, MissingDwarfInfoError


class TestElfLoader(unittest.TestCase):
    """Test cases for loading of elf file"""

    @unittest.skip('elftoos do not detect lack of dwarf comments correctly')
    def test_dwarf_info_missing(self):
        """Checks if program detects lack of dwarf comments"""
        MISSING_DWARF_INFO_FILE = 'tests/testfiles/test_no_dwarf.elf'
        self.assertRaises(MissingDwarfInfoError, ELFData, MISSING_DWARF_INFO_FILE)

    def test_correct_parse_single_file(self):
        """Checks if program parses correct file without errors"""
        TEST_FILE = 'tests/testfiles/test_code.elf'
        ELFData(TEST_FILE)

    def test_correct_parse_multiple_files(self):
        """Checks if program parses correct file without errors (multiple CUs)"""
        TEST_FILE = 'tests/testfiles/test_code_multi.elf'
        ELFData(TEST_FILE)
