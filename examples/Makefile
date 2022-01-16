CC = gcc
CFLAGS = -gdwarf-4
DBUSFLAGS = -I/usr/include/dbus-1.0 -I/usr/lib/dbus-1.0/include -I/usr/include/glib-2.0 -I/usr/lib/glib-2.0/include -ldbus-glib-1 -ldbus-1 -lgobject-2.0 -lglib-2.0

program: program.c
	$(CC) $< -o $@ $(CFLAGS) $(DBUSFLAGS)

clean:
	rm -f program
	rm -rf generated

.PHONY: all clean
