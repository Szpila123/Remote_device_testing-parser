from typing import Type
import ctypes


types_map: dict[str, Type] = {

    '_Bool': 'c_bool',
    'char': 'c_char',
    'signed char': 'c_char',
    'wchar_t': 'c_wchar',
    'unsigned char': 'c_ubyte',
    'short': 'c_short',
    'short int': 'c_short',
    'unsigned short': 'c_ushort',
    'short unsigned int': 'c_ushort',
    'int': 'c_int',
    'unsigned int': 'c_uint',
    'long': 'c_long',
    'long int': 'c_long',
    'unsigned long': 'c_ulong',
    'long unsigned int': 'c_ulong',
    'long long': 'c_longlong',
    'long long int': 'c_longlong',
    'long long unsigned int': 'c_longlong',
    '__int64': 'c_longlong',
    'unsigned long long': 'c_ulonglong',
    'unsigned long long int': 'c_ulonglong',
    'unsigned __int64': 'c_ulonglong',
    'size_t': 'c_size_t',
    'sszie_t': 'c_ssize_t',
    'float': 'c_float',
    'double': 'c_double',
    'long double': 'c_longdouble'
}

size_map: dict[int: Type] = {
    1: 'c_ubyte',
    2: 'c_ushort',
    4: 'c_uint'
}

GENERATED_FILE_IMPORTS = f"""
from ctypes import {', '.join(types_map.values())}, Union, Structure
from backend import Enum, PointerClass, Variable, Function, FunctionType, Void

"""
