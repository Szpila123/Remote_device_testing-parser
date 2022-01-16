#include <stdint.h>

int external_function(int a)
{
    return a + 3;
}

int global_var;

static int static_var;


struct LocalStruct
{
    int l1;
    char l2;
    void* l3;
};

static int32_t local_function(struct LocalStruct w)
{
    w.l1 += 12;
    return w.l2 + 33;
}
