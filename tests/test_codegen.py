import unittest
from elf.elfdata import ELFData, MissingDwarfInfoError


class TestCodeGeneration(unittest.TestCase):
    """Test cases for generating python code"""

    def test_generate_code_single_file(self):
        """Tests if code generation rises any errors (single CU)"""
        TEST_FILE = 'tests/testfiles/test_code.elf'
        file_list = ELFData(TEST_FILE).parse_elffile()
        self.assertEqual(len(file_list), 1, 'Expected single file object of single CU elf')
        self.assertEqual(file_list[0].filename, 'test_code_c.py', 'Wrong filename')
        self.assertNotEqual(file_list[0].generate_code(), '')

    def test_generate_code_multiple_files(self):
        """Tests if code generation rises any errors (multiple CUs)"""
        TEST_FILE = 'tests/testfiles/test_code_multi.elf'
        file_list = ELFData(TEST_FILE).parse_elffile()
        self.assertEqual(len(file_list), 2, 'Expected two file objects of elf with two CUs')
        for file in file_list:
            self.assertIn(file.filename, ['test_code_multi_main_c.py', 'test_code_multi_header_c.py'], 'Wrong filename')
            self.assertNotEqual(file_list[0].generate_code(), '')
