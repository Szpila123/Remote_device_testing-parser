#!/usr/bin/python

import sys
import os
import pathlib
import logging
import argparse
import inspect

import elf.elfdata as elfdata

import program.generator.generator_backend as backend

from common.exceptions import FileWriteError

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
    parser.add_argument('--print',
                        help='Print code output instead of saving to file',
                        action='store_true')
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

    # Load and parse elf file, generate output
    error_prefix = 'Error while parsing elf file'
    try:
        efile = elfdata.ELFData(args.elffile)
        program_files = efile.parse_elffile()
        if args.print:
            print(*(file.generate_code() for file in program_files))
        else:
            if not os.path.exists(args.dst):
                os.makedirs(args.dst)

            for file in program_files:
                file.generate_file(args.dst)

            backend_code = inspect.getsource(backend)
            with open(args.dst / 'backend.py', 'w') as file:
                written = file.write(backend_code)
                if written < len(backend_code):
                    raise FileWriteError('Could not write backend code completly')

    except OSError as error:
        logging.error(f' {error_prefix}: {error.filename} - {error.strerror}')
        return error.errno

    except Exception as error:
        logging.exception(f' {error_prefix}')
        return os.EX_SOFTWARE

    return os.EX_OK


if __name__ == '__main__':
    sys.exit(main())
