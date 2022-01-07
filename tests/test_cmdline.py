import io
import unittest
import argparse
import sys
import logging

from parser import main, parse_args, VERSION


class TestCommandLine(unittest.TestCase):
    """Test cases for command line interface of parser.py"""

    def setUp(self) -> None:
        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

    def tearDown(self) -> None:
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
