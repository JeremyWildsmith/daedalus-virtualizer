#include "test_helper.h"

void main()
{
    int a, b, c, d;
    a = 2, b = 3;

    ASSERT(a == 2);
    ASSERT(b == 3);

    print_testpass();
}