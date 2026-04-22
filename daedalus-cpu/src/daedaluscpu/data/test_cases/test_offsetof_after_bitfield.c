#include "test_helper.h"

struct z
{
    char foo : 1;
    int fu : 2;
    int bar;
};

void do_x(struct z g)
{
    print_str("do_x was called\n");
}

void main()
{
    unsigned off = __builtin_offsetof(struct z, bar);
    ASSERT(off != 0);

    struct z y;
    do_x(y);

    print_testpass();
}