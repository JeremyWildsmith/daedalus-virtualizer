#include "test_helper.h"

int test_function(int, int c)
{
    int stack[2] = { 0xAAAAAA, 0xBBBBBB };
    struct { int ptr; } v;
    struct
    {
        int ptr;
    } *s = &v;
    s->ptr = 2;

    int d;
    d = ((20 + c * 10 + c) >> 2) - 123;
    print_hex(d, 8);
    print_str("\n");
    d = stack[--s->ptr];
    --d;
    d--;
    return d;
}

void main() {
    int r = test_function(10, 11);
    print_hex(r, 8);
    print_testpass();
}