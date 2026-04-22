#include "test_helper.h"
struct z
{
    int foo;
    int bar;
};

void main()
{
    unsigned int offset = __builtin_offsetof(struct z, foo);
    ASSERT(offset == 0);
    
    unsigned int offset_bar = __builtin_offsetof(struct z, bar);
    ASSERT(offset_bar != 0);

    struct z test;
    test.bar = 0;

    int* p = (int*)((char*)&test + offset_bar);
    *p = 10;

    ASSERT(test.bar == 10);

    print_testpass();
}