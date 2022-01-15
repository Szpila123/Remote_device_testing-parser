#include <stdio.h>

typedef struct TestStruct_tag
{
    int a;
    char b;
    void *c;
} TestStruct_t;

struct BitFields
{
    int a : 1;
    int b : 2;
    int c : 3;
    int d : 2;
};

enum Values
{
    VAL_FIRST = 0,
    VAL_SECOND = 3
};

union Unity
{
    char (*function_ptr)(int, char);
    int c;
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

    printf("%c\n", test_function(1));
    printf("%d\n", VAL_FIRST);
    printf("%d\n", a.function_ptr(3, 'a'));

    return 0;
}
