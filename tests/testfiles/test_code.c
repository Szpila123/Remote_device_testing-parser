#include <stdio.h>

typedef struct TestStruct_tag
{
    int a;
    char b;
    void *c;
} TestStruct_t;

struct BitFields
{
    int bitf1 : 1;
    int bitf2 : 2;
    int bitf3 : 3;
    int bitf4 : 2;
};

enum Values
{
    VAL_FIRST = 0,
    VAL_SECOND = 3,
    VAL_THIRD
};

union Unity
{
    char (*function_ptr)(int, char);
    int union_int;
};

TestStruct_t structs[3] = {
    (TestStruct_t){.a = 1, .b = 'a', .c = 0},
    (TestStruct_t){.a = 2, .b = 'b', .c = 0},
    (TestStruct_t){.a = 3, .b = 'c', .c = 0},
};

char test_function(size_t elem)
{
    return structs[elem].b;
}

static char static_function(int count, char character)
{
    return character + count;
}

char (*my_pointer)(int, char) = static_function;

int main(int argc, char *argv[])
{
    union Unity a = {.function_ptr = my_pointer};
    struct BitFields bf;

    printf("%c\n", test_function(1));
    printf("%d\n", VAL_FIRST);
    printf("%d\n", a.function_ptr(3, 'a'));

    bf.bitf1 = 0b0;
    bf.bitf2 = 0b10;
    bf.bitf3 = 0b101;
    bf.bitf4 = 0b01;
    printf("%d\n", *((int*) &bf));
    printf("%p\n", &my_pointer);
    printf("%p\n", static_function);

    return 0;
}
