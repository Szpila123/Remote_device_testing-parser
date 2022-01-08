import io
import unittest
import argparse
import sys

from parser import init_logging, parse_args, VERSION


class TestCommandLine(unittest.TestCase):
    """Test cases for command line interface of parser.py"""

    def setUp(self) -> None:
        """Substitute stdout and stderr with StringIO to capture argparse output"""
        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

    def tearDown(self) -> None:
        """Revert stdout and stderr"""
        sys.stdout = self.orig_stdout
        sys.stderr = self.orig_stderr

    @unittest.skip('argparse ignored exit_on_error parameter, will fix later')
    def test_parameter_missing(self):
        """Checks if program reports missing parameter correctly"""
        arg_groups = ([], ['--dst', 'out'])

        for args in arg_groups:
            with self.subTest(args=args):
                with self.assertRaises(argparse.ArgumentError) as cm:
                    parse_args(args)
                self.assertIn(cm.exception.message, 'the following arguments are required: elffile')

    @unittest.skip('argparse ignored exit_on_error parameter, will fix later')
    def test_parameter_incorrect(self):
        """Checks if program detects non-existent file"""
        arg_groups = (['-z'], ['out', '--memory'], ['--hel'])

        for args in arg_groups:
            with self.subTest(args=args):
                with self.assertRaises(argparse.ArgumentError) as cm:
                    parse_args(args)
                self.assertIn(cm.exception.message, 'the following arguments are required: elffile')

    def test_help(self):
        """Checks if program help message prints correctly"""
        arg_groups = (['-h'], ['--help'])

        for args in arg_groups:
            with self.subTest(args=args):
                self.assertRaises(SystemExit, parse_args, args)
                self.assertIn('usage:', sys.stdout.getvalue())

    def test_version(self):
        """Checks if program version prints correctly"""
        arg_groups = (['--version'],)

        for args in arg_groups:
            with self.subTest(args=args):
                self.assertRaises(SystemExit, parse_args, args)
                self.assertIn(f'{VERSION}', sys.stdout.getvalue())

    def test_arguments_ok(self):
        """Check if program parses good arguments correctly"""
        elffile = 'tests/testfiles/test_code.elf'
        arg_groups = (['-v', elffile], ['--dst', 'catalog', elffile], ['-vvv', elffile],
                      [elffile, '--verbose', '--dst', 'dst'], [elffile, '--log', 'log'])

        for args in arg_groups:
            with self.subTest(args=args):
                self.assertIsInstance(parse_args(args), argparse.Namespace, 'Arguments did not parse correctly')

    def test_verbosity(self):
        """Checks if program count verbosity level correctly"""
        elffile = 'tests/testfiles/test_code.elf'
        arg_groups = ((1, ['-v', elffile]), (1, ['--verbose', elffile]), (3, ['-vvv', elffile]), (0, [elffile]))

        for verbose_count, args in arg_groups:
            with self.subTest(args=args):
                parsed_args = parse_args(args)
                self.assertEqual(parsed_args.verbose, verbose_count, 'Verbosity count does not match')
                # TODO: check if log levels print correctly
