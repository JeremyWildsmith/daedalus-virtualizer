#include "test_helper.h"

int a;
int b = 20;

void main()
{
    a = 10 + b;
    ASSERT(a == 30);

    print_testpass();
}