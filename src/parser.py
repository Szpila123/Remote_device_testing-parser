#!/usr/bin/python
import sys
import os
import pathlib
import logging
import argparse

import elf.elffile as elffile

VERSION = '0.0.1'


def create_args_parser() -> argparse.ArgumentParser:
    """Create parser for command line"""

    parser = argparse.ArgumentParser(description='Program generating code representation from elf file in python',
                                     exit_on_error=False)

    parser.add_argument('elffile',
                        type=pathlib.Path,
                        help='Elffile with dwarf debug information',
                        action='store')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + VERSION)
    parser.add_argument('-d',
                        '--dst',
                        type=pathlib.Path,
                        help='Destination cataloge of parser output',
                        default=pathlib.Path('.') / 'output',
                        action='store')
    return parser


def parse_args(args: list[str]) -> argparse.Namespace:
    """Parse given arguements"""
    return create_args_parser().parse_args(args)


def main():
    """Parse arguments"""
    try:
        args = parse_args(sys.argv[1:])
    except argparse.ArgumentError as error:
        logging.error(error.message)
        return os.EX_USAGE

    """Load and parse elf file"""
    error_prefix = 'Error while parsing elf file'
    try:
        with open(args.elffile, 'rb') as file:
            efile = elffile.load_elffile(file)

    except OSError as error:
        logging.error(f' {error_prefix}: {error.filename} - {error.strerror}')
        return error.errno

    except Exception as error:
        logging.exception(f' {error_prefix}')
        return os.EX_SOFTWARE

    return os.EX_OK


if __name__ == '__main__':
    sys.exit(main())
