import sys
import os
import argparse


def create_args_parser() -> argparse.ArgumentParser:
    '''Create parser for command line'''
    parser = argparse.ArgumentParser(description='Program for simplifing text')
    parser.add_argument('elffile',
                        type=str,
                        help='Elffile with dwarf debug information',
                        action='store')
    parser.add_argument('-d',
                        '--dst',
                        type=str,
                        help='Destination cataloge of parser output',
                        default=os.path.join('..', 'output'),
                        action='store')
    return parser


if __name__ == '__main__':

    '''Parse arguments'''
    arg_parser = create_args_parser()
    args = arg_parser.parse_args(sys.argv[1:])

    exit(0)
