#include <stdio.h>
#include "test_code_multi_header.h"



int main(int argc, char *argv[])
{
    int my_var = external_function(22);
    printf("%d\n", my_var);

    return 0;
}
