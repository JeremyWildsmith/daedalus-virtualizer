#include "test_helper.h"

void main()
{
    enum E
    {
        A,
        B,
        C
    };
    enum D
    {
        X,
        Y,
        Z
    };
    enum E e = Z;

    ASSERT(e == C);

    print_testpass();
}