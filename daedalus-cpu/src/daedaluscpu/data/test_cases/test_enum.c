#include "test_helper.h"

void main()
{
    enum E
    {
        A,
        B,
        C = A + 10
    };

    enum E e = A;

    ASSERT(e == 0);

    e = B;

    ASSERT(e == 1);
    
    e = 10;

    ASSERT(e == C);

    print_testpass();
}