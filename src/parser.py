#!/usr/bin/python
import sys
import os
import pathlib
import logging
import argparse

import elf.elfdata as elfdata

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
    parser.add_argument('--log',
                        type=pathlib.Path,
                        help='Save logs to given file',
                        action='store')
    parser.add_argument('-v',
                        '--verbose',
                        default=0,
                        help='Increase verbosity level of arguments',
                        action='count')
    return parser


def parse_args(args: list[str]) -> argparse.Namespace:
    """Parse given arguements"""
    return create_args_parser().parse_args(args)


def init_logging(filename: pathlib.Path, verbosity: int) -> None:
    """Initialize logging configuration"""
    LOG_LEVEL_STEP = 10
    LOG_FORMAT = '%(module)s:%(levelname)s: %(message)s'
    log_level = logging.ERROR - verbosity * LOG_LEVEL_STEP

    logging.basicConfig(format=LOG_FORMAT, filename=filename, level=log_level)
    logging.info(f'Verbosity level: {verbosity}')


def main() -> int:
    """Main program procedure"""

    # Parse arguments
    try:
        args = parse_args(sys.argv[1:])
    except argparse.ArgumentError as error:
        logging.error(error.message)
        return os.EX_USAGE

    # Initialize logging module
    try:
        init_logging(args.log, args.verbose)

    except FileNotFoundError as error:
        logging.error(f' Error while trying to open logging file {error.filename} - {error.strerror}')
        return error.errno

    # Load and parse elf file
    error_prefix = 'Error while parsing elf file'
    try:
        efile = elfdata.ELFData(args.elffile)

    except OSError as error:
        logging.error(f' {error_prefix}: {error.filename} - {error.strerror}')
        return error.errno

    except Exception as error:
        logging.exception(f' {error_prefix}')
        return os.EX_SOFTWARE

    return os.EX_OK


if __name__ == '__main__':
    sys.exit(main())
