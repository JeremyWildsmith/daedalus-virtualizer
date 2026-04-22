#include "test_helper.h"

void main(void)
{
    int a=100, b=5, c=2;

    a += b - c;
    ASSERT(a == 103);

    a -= b - c;
    ASSERT(a == 100);

    a /= b - c;
    ASSERT(a == 33);

    a %= b - c;
    ASSERT(a == 0);

    a |= b - c;
    ASSERT(a == 3);

    a &= 9;
    ASSERT(a == 1);

    ASSERT(b == 5);
    ASSERT(c == 2);

    print_testpass();
}