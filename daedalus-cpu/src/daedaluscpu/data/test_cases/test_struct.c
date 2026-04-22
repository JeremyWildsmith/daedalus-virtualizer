#include "test_helper.h"

typedef struct {int quot, rem; } div_t;

void main() {
    div_t x, *y;
    x.rem = 2;
    y = &x;
    y->quot = 4;

    ASSERT(x.rem == 2 && x.quot == 4);

    print_testpass();
}