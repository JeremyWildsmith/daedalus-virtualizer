#include "test_helper.h"

union z
{
    int foo;
    struct
    {
        int b;
    };
};

void main()
{
    union z my_z;
    my_z.b = 34;
    ASSERT(my_z.b == 34);

    print_testpass();
}