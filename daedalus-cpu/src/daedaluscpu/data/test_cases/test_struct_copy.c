#include "test_helper.h"

typedef struct { int a,b,c,d,e,f; } data_t;

data_t my_f(data_t y) {
    data_t z;

    z.a = y.a;
    z.b = 500;
    z.c = y.c;
    z.d = y.d;
    z.e = y.e;
    z.f = y.f;
    return z;
}

void main(void) {
    data_t buf[3];

    buf[0].a = 1;  buf[0].b = 2;  buf[0].c = 3;  buf[0].d = 4;  buf[0].e = 5;  buf[0].f = 6;
    buf[1].a = 10; buf[1].b = 20; buf[1].c = 30; buf[1].d = 40; buf[1].e = 50; buf[1].f = 60;
    buf[2].a = 100;buf[2].b = 200;buf[2].c = 300;buf[2].d = 400;buf[2].e = 500;buf[2].f = 600;

    data_t *ptr = buf;
    data_t x;

    x = *ptr++;
    print_str("a\n");
    ASSERT(x.a == 1);
    print_str("b\n");
    ASSERT(x.b == 2);
    print_str("c\n");
    ASSERT(ptr == &buf[1]);

    x = my_f(x);
    print_str("d\n");
    ASSERT(x.a == 1);
    print_str("e\n");
    ASSERT(x.b == 500);
    print_str("f\n");
    ASSERT(x.c == 3);
    print_str("g\n");
    ASSERT(x.f == 6);

    x = my_f(*ptr--);
    print_str("h\n");
    ASSERT(x.a == 10);
    print_str("i\n");
    ASSERT(x.b == 500);
    print_str("j\n");
    ASSERT(x.c == 30);
    print_str("k\n");
    ASSERT(ptr == &buf[0]);

    print_testpass();
}
