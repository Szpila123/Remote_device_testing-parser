#include <stdio.h>

typedef struct TestStruct_tag
{
    int a;
    char b;
    void *c;
} TestStruct_t;

enum Values {
    VAL_FIRST = 0,
    VAL_SECOND = 3
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

int main(int argc, char *argv[])
{
    printf("%c\n", test_function(1));
    printf("%d\n", VAL_FIRST);

    return 0;
}
