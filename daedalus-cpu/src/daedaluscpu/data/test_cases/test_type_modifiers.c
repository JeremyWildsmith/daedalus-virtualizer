#include "test_helper.h"

void main() {
    char x, *y;
    const int* const_ptr = 0;
    volatile int* vol_ptr = 0;

    ASSERT(sizeof(x) == 1);
    ASSERT(sizeof(y) == sizeof(int*) && sizeof(y) != 1);

    ASSERT(sizeof(const_ptr) == sizeof(int*));
    ASSERT(sizeof(vol_ptr) == sizeof(int*));

    print_testpass();
}