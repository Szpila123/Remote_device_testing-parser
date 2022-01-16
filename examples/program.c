#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>

#include <dbus/dbus.h>
#include <dbus/dbus-glib-lowlevel.h>

#define INTERFACE "org.example.TestsInterface"

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
    "      <arg name='address' direction='in' type='i'/>\n"
    "      <arg name='size' direction='in' type='s'/>\n"
    "      <arg name='value' direction='in' type='s'/>\n"
    "    </method>\n"
    "    <method name='Read'>\n"
    "      <arg name='address' direction='in' type='i'/>\n"
    "      <arg name='size' direction='in' type='s'/>\n"
    "      <arg type='s' direction='out' />\n"
    "    </method>\n"
    "    <method name='Execute'>\n"
    "      <arg name='address' direction='in' type='i'/>\n"
    "      <arg name='args' direction='in' type='s'/>\n"
    "      <arg type='s' direction='out' />\n"
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
        const char *pong = "Pong";

        if (!(reply = dbus_message_new_method_return(message)))
            goto fail;

        dbus_message_append_args(reply, DBUS_TYPE_STRING, &pong, DBUS_TYPE_INVALID);
    }
    else if (dbus_message_is_method_call(message, INTERFACE, "Read"))
    {
        const char *msg;

        if (!dbus_message_get_args(message, &err, DBUS_TYPE_STRING, &msg, DBUS_TYPE_INVALID))
            goto fail;

        if (!(reply = dbus_message_new_method_return(message)))
            goto fail;

        dbus_message_append_args(reply, DBUS_TYPE_STRING, &msg, DBUS_TYPE_INVALID);
    }
    else if (dbus_message_is_method_call(message, INTERFACE, "Execute"))
    {

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
