#include "test_helper.h"

void main()
{
    int a = 2, b = 4, c, d = 3;
    c = 6;
    ASSERT(c == 6);

    d = a + b - c / a * b;
    ASSERT(d == -6);
    d = !a;

    ASSERT(d == 0);

    d = a ? b : c + 2;

    ASSERT(d == 4);

    print_testpass();
}
