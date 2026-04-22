#include "test_helper.h"

typedef int a;

int add(a a)
{
a:
    return a + 10;
}

void main() {
    ASSERT(add(5) == 15)
    
    print_testpass();

    return;
}