#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#include <dbus/dbus.h>
#include <dbus/dbus-glib-lowlevel.h>

#define INTERFACE "org.example.TestsInterface"
#define MESSAGE_SIZE 64

static char buffer[64] = "Hello";

GMainLoop *glibMain;
const char *introspection =
    DBUS_INTROSPECT_1_0_XML_DOCTYPE_DECL_NODE
    "<node>\n"

    "  <interface name='org.freedesktop.DBus.Introspectable'>\n"
    "    <method name='Introspect'>\n"
    "      <arg name='data' type='s' direction='out' />\n"
    "    </method>\n"
    "  </interface>\n"

    "  <interface name='org.example.TestsInterface'>\n"
    "    <property name='Version' type='s' access='read' />\n"
    "    <method name='Write' >\n"
    "      <arg name='address' direction='in' type='t'/>\n"
    "      <arg name='size' direction='in' type='t'/>\n"
    "      <arg name='value' direction='in' type='ay'/>\n"
    "      <arg type='s' direction='out' />\n"
    "    </method>\n"
    "    <method name='Read'>\n"
    "      <arg name='address' direction='in' type='t'/>\n"
    "      <arg name='size' direction='in' type='t'/>\n"
    "      <arg type='ay' direction='out' />\n"
    "    </method>\n"
    "    <method name='Execute'>\n"
    "      <arg name='address' direction='in' type='t'/>\n"
    "      <arg name='args' direction='in' type='ay'/>\n"
    "      <arg type='t' direction='out' />\n"
    "    </method>\n"
    "  </interface>\n"

    "</node>\n";

DBusHandlerResult test_interface(DBusConnection *conn, DBusMessage *message, void *data)
{
    DBusHandlerResult result;
    DBusMessage *reply = NULL;
    DBusError err;

    dbus_error_init(&err);
    if (dbus_message_is_method_call(message, DBUS_INTERFACE_INTROSPECTABLE, "Introspect"))
    {

        if (!(reply = dbus_message_new_method_return(message)))
            goto fail;

        dbus_message_append_args(reply, DBUS_TYPE_STRING, &introspection, DBUS_TYPE_INVALID);
    }
    else if (dbus_message_is_method_call(message, INTERFACE, "Write"))
    {
        int64_t size, address;
        char value[MESSAGE_SIZE];
        char *pValue = value;

        if (!dbus_message_get_args(message, &err, DBUS_TYPE_UINT64, &address,
                                   DBUS_TYPE_UINT64, &size, DBUS_TYPE_ARRAY, DBUS_TYPE_BYTE,
                                   &pValue, MESSAGE_SIZE, DBUS_TYPE_INVALID))
            goto fail;

        if (size > MESSAGE_SIZE)
        {
            size = MESSAGE_SIZE;
        }
        memcpy((void *)address, value, size);

        if (!(reply = dbus_message_new_method_return(message)))
            goto fail;

        dbus_message_append_args(reply, DBUS_TYPE_STRING, "OK", DBUS_TYPE_INVALID);
    }
    else if (dbus_message_is_method_call(message, INTERFACE, "Read"))
    {
        int64_t size, address;
        char value[MESSAGE_SIZE];
        char *pValue = value;

        if (!dbus_message_get_args(message, &err, DBUS_TYPE_UINT64, &address,
                                   DBUS_TYPE_UINT64, &size, DBUS_TYPE_INVALID))
            goto fail;

        if (size > MESSAGE_SIZE)
            size = MESSAGE_SIZE;

        memcpy(value, (void *)address, size);

        if (!(reply = dbus_message_new_method_return(message)))
            goto fail;

        dbus_message_append_args(reply, DBUS_TYPE_ARRAY, DBUS_TYPE_BYTE, &pValue, size, DBUS_TYPE_INVALID);
    }
    else if (dbus_message_is_method_call(message, INTERFACE, "Execute"))
    {
        int64_t address, retval;
        char args[MESSAGE_SIZE];
        char *pArgs = args;

        if (!dbus_message_get_args(message, &err, DBUS_TYPE_UINT64, &address,
                                   DBUS_TYPE_ARRAY, DBUS_TYPE_BYTE, &pArgs, MESSAGE_SIZE, DBUS_TYPE_INVALID))
            goto fail;

        // Decode args and execute function
        retval = 0;

        if (!(reply = dbus_message_new_method_return(message)))
            goto fail;

        dbus_message_append_args(reply, DBUS_TYPE_INT64, &retval, DBUS_TYPE_INVALID);
    }
    else
        return DBUS_HANDLER_RESULT_NOT_YET_HANDLED;

fail:
    if (dbus_error_is_set(&err))
    {
        if (reply)
            dbus_message_unref(reply);
        reply = dbus_message_new_error(message, err.name, err.message);
        dbus_error_free(&err);
    }
    if (!reply)
        return DBUS_HANDLER_RESULT_NEED_MEMORY;

    result = DBUS_HANDLER_RESULT_HANDLED;
    if (!dbus_connection_send(conn, reply, NULL))
        result = DBUS_HANDLER_RESULT_NEED_MEMORY;
    dbus_message_unref(reply);

    return result;
}

const DBusObjectPathVTable vtable = {.message_function = test_interface};

int main(void)
{
    DBusConnection *conn;
    DBusError err;
    int ret;

    dbus_error_init(&err);

    conn = dbus_bus_get(DBUS_BUS_SESSION, &err);
    if (!conn)
    {
        fprintf(stderr, "DBus session fail %s\n", err.message);
        goto fail;
    }

    ret = dbus_bus_request_name(conn, "org.example.Program", DBUS_NAME_FLAG_REPLACE_EXISTING, &err);
    if (ret != DBUS_REQUEST_NAME_REPLY_PRIMARY_OWNER)
    {
        fprintf(stderr, "Failed to request name on bus");
        goto fail;
    }

    if (!dbus_connection_register_object_path(conn, "/org/example/Program", &vtable, NULL))
    {
        fprintf(stderr, "Failed to register object path");
        goto fail;
    }

    glibMain = g_main_loop_new(NULL, false);
    dbus_connection_setup_with_g_main(conn, NULL);
    g_main_loop_run(glibMain);

    return EXIT_SUCCESS;
fail:
    dbus_error_free(&err);
    return EXIT_FAILURE;
}
