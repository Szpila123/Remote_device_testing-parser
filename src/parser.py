#!/usr/bin/python
import sys
import os
import pathlib
import logging
import argparse

import elf.elffile as elffile


def create_args_parser() -> argparse.ArgumentParser:
    """Create parser for command line"""

    parser = argparse.ArgumentParser(description='Program generating code representation from elf file in python')

    parser.add_argument('elffile',
                        type=pathlib.Path,
                        help='Elffile with dwarf debug information',
                        action='store')
    parser.add_argument('-d',
                        '--dst',
                        type=pathlib.Path,
                        help='Destination cataloge of parser output',
                        default=pathlib.Path('.') / 'output',
                        action='store')
    return parser


if __name__ == '__main__':

    """Parse arguments"""
    arg_parser = create_args_parser()
    args = arg_parser.parse_args(sys.argv[1:])

    """Load and parse elf file"""
    error_prefix = 'Error while parsing elf file'
    try:
        with open(args.elffile, 'rb') as file:
            efile = elffile.load_elffile(file)

    except OSError as error:
        logging.error(f' {error_prefix}: {error.filename} - {error.strerror}')
        sys.exit(error.errno)

    except Exception as error:
        logging.exception(f' {error_prefix}')
        sys.exit(os.EX_SOFTWARE)

    exit(os.EX_OK)
