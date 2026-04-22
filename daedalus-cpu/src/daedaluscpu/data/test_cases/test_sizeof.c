#include "test_helper.h"

void main(void)
{
    int x, *y;
    union U;
    union U
    {
        int x;
    };

    union U u;

    x = sizeof *y;
    ASSERT(x > 0 && x < 8 && x == sizeof(int))

    x = sizeof(*y);
    ASSERT(x > 0 && x < 8 && x == sizeof(int))

    x = sizeof(union U);
    ASSERT(x > 0 && x < 8 && x == sizeof(int))

    int w = sizeof w; // Sizeof works on the expression before the '='
    ASSERT(w > 0 && w < 8 && w == sizeof(int))

    print_testpass();
}