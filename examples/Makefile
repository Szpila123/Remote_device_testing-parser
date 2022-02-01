CC = gcc
CFLAGS = -gdwarf-4
DBUSFLAGS = -I/usr/include/dbus-1.0 -I/usr/lib/dbus-1.0/include -I/usr/include/glib-2.0 -I/usr/lib/glib-2.0/include -ldbus-glib-1 -ldbus-1 -lgobject-2.0 -lglib-2.0

run_test: | run clean

program: program.c
	$(CC) $< -o $@ $(CFLAGS) $(DBUSFLAGS)

generate: program
	../src/parser.py program --dst generated
	../src/parser.py program --onlybackend --dst .
	touch generated/__init__.py

clean:
	rm -f program
	rm -f backend.py
	rm -rf generated

run: generate
	setarch x86_64 -R ./program &
	./test_framework.py
	killall program

.PHONY: all clean run generate tun_test
