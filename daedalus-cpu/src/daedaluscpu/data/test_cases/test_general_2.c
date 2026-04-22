#include "test_helper.h"

static int c=2, d=4, e=8;
static long x;

void main()
{
    int d;
    d = 20 + c * 10 + (c >> 2) - 123;
    print_hex(d, 8);
    print_str("\n");

    ASSERT(d == -83);

    print_testpass();
}