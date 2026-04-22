#include "test_helper.h"

struct rec
{
    struct
    {
        int x;
    };
};

struct rec d = {.x = 2};

void main()
{
    struct rec d = {.x = 2};
    ASSERT(d.x == 2);
    print_testpass();
}