#include "test_helper.h"

void f(int n)
{
    struct S
    {
        int a;
    } s;
    union U
    {
        int a;
    } u;
    enum E
    {
        E1,
        E2
    } e;
    if (n == 10)
    {
        print_str("If clause entered.\n");
        struct S
        {
            int b;
        } s;
        s.b = 1;
        union U
        {
            int b;
        } u;
        u.b = 1;
        enum E
        {
            E3,
            E4
        } e;
        e = E3;

        print_hex(s.b, 8);
        print_str("\n");
        print_hex(u.b, 8);
        print_str("\n");
        print_hex(e, 8);
        print_str("\n");
    }
    s.a = 2;
    u.a = 2;
    e = E1;

    print_hex(s.a, 8);
    print_str("\n");
    print_hex(u.a, 8);
    print_str("\n");
    print_hex(e, 8);
    print_str("\n");
}

void main() {
    print_str("Call 1\n");
    f(0);
    print_str("Call 2\n");
    f(10);
    print_testpass();
}