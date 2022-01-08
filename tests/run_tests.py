#!/usr/bin/python
import unittest
import sys
import os
import logging
import pathlib

PROJECT_DIR = 'Remote_device_testing-parser'
TEST_DIR = 'tests'
SRC_DIR = 'src'


def main(args: list[str]):
    curdir = pathlib.Path(os.path.realpath(os.curdir))
    if os.path.basename(curdir) != PROJECT_DIR or not os.path.exists(TEST_DIR):
        logging.error(f'Tests should be run from main directory of repository')
        return 1

    else:
        sys.path += [str(curdir / SRC_DIR)]
        tests = unittest.TestLoader().discover(TEST_DIR, 'test*.py', TEST_DIR)
        verbosity = ''.join(args).count('v')
        result = unittest.TextTestRunner(verbosity=verbosity).run(tests)
        return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
