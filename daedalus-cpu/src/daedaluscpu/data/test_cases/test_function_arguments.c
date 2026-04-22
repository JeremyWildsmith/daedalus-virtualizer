#include "test_helper.h"

int add(int a, int b, int c) {
    return a + b + c;
}

void main()
{
    ASSERT(add((int)22, 2, 3) == 27);
    print_testpass();
}