#include "test_helper.h"

typedef struct
{
    int x;
} X_t;

static X_t test_func(void)
{
    return (X_t){2};
}

void main(void)
{
    X_t v = test_func();
    ASSERT(v.x == 2);
    print_testpass();
}