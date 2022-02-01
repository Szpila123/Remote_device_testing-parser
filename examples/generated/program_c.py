
from ctypes import c_bool, c_char, c_char, c_wchar, c_ubyte, c_short, c_short, c_ushort, c_ushort, c_int, c_uint, c_long, c_long, c_ulong, c_ulong, c_longlong, c_longlong, c_longlong, c_longlong, c_ulonglong, c_ulonglong, c_ulonglong, c_size_t, c_ssize_t, c_float, c_double, c_longdouble, Union, Structure
from backend import Enum, PointerClass, Variable, Function, FunctionType, Void


class Unnamed_type_0(c_uint, Enum):
    _type = c_uint
    DBUS_BUS_SESSION = 0
    DBUS_BUS_SYSTEM = 1
    DBUS_BUS_STARTER = 2


class Unnamed_type_1(c_uint, Enum):
    _type = c_uint
    DBUS_HANDLER_RESULT_HANDLED = 0
    DBUS_HANDLER_RESULT_NOT_YET_HANDLED = 1
    DBUS_HANDLER_RESULT_NEED_MEMORY = 2


size_t = c_ulong

_normalize___int64_t = c_long

int64_t = _normalize___int64_t

c_char_array_32 = c_char * 32
dbus_uint32_t = c_uint

dbus_bool_t = dbus_uint32_t


class DBusError(Structure):
    _fields_ = [
        ('name', PointerClass(1)),
        ('message', PointerClass(1)),
        ('dummy1', c_uint),
        ('dummy2', c_uint),
        ('dummy3', c_uint),
        ('dummy4', c_uint),
        ('dummy5', c_uint),
        ('padding1', PointerClass(8)),
    ]


class FunctionType_394(FunctionType):
    _return_type = Void
    _args = []


class DBusMessage(Structure):
    _fields_ = [
    ]


DBusBusType = Unnamed_type_0

DBusHandlerResult = Unnamed_type_1


class DBusConnection(Structure):
    _fields_ = [
    ]


class FunctionType_707(FunctionType):
    _return_type = Void
    _args = [PointerClass(8)]


DBusObjectPathMessageFunction = PointerClass(8)

gint = c_int

gboolean = gint


class _GMainContext(Structure):
    _fields_ = [
    ]


class _GMainLoop(Structure):
    _fields_ = [
    ]


c_char_array_64 = c_char * 64
DBusError = DBusError

DBusMessage = DBusMessage

DBusConnection = DBusConnection


class FunctionType_657(FunctionType):
    _return_type = DBusHandlerResult
    _args = [PointerClass(8), PointerClass(8), PointerClass(8)]


DBusObjectPathUnregisterFunction = PointerClass(8)

GMainContext = _GMainContext

GMainLoop = _GMainLoop


class DBusObjectPathVTable(Structure):
    _fields_ = [
        ('unregister_function', DBusObjectPathUnregisterFunction),
        ('message_function', DBusObjectPathMessageFunction),
        ('dbus_internal_pad1', PointerClass(8)),
        ('dbus_internal_pad2', PointerClass(8)),
        ('dbus_internal_pad3', PointerClass(8)),
        ('dbus_internal_pad4', PointerClass(8)),
    ]


DBusObjectPathVTable = DBusObjectPathVTable


class Code(object):
    def __init__(self):
        self.buffer = Variable(0x40e0, c_char_array_32)
        self.glibMain = Variable(0x4110, PointerClass(8))
        self.introspection = Variable(0x4100, PointerClass(1))
        self.vtable = Variable(0x3d80, DBusObjectPathVTable)

        self.main = Function(0x16ec, [], c_int)
        self.test_interface = Function(0x1259, [PointerClass(8), PointerClass(8), PointerClass(8)], DBusHandlerResult)
