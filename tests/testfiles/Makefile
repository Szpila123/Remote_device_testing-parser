# Automation of test code building
CC = gcc
DWARF_FLAGS = -gdwarf-4
NO_DWARF_FLAGS = -g0

objects = test_no_dwarf.elf test_code.elf test_code_multi.elf

all: $(objects)

test_code.elf: test_code.c
	$(CC) $(DWARF_FLAGS) $^ -o $@

test_no_dwarf.elf: test_code.c
	$(CC) $(NO_DWARF_FLAGS) $^ -o $@

test_code_multi.elf: test_code_multi_main.c test_code_multi_header.c
	$(CC) $(DWARF_FLAGS) $^ -o $@

clean:
	rm *.elf

.PHONY: all clean
