#include "test_helper.h"

void main(void) {
    char anchor;
    char *a = &anchor;
    char *c;

    c = a + 10;
    if ((c - a) != 10) { print_testfail(); return; }

    c = 20 + a;
    if ((c - a) != 20) { print_testfail(); return; }

    a = a - 10;
    if ((&anchor - a) != 10) { print_testfail(); return; }

    a += 2;
    a -= 4;
    if ((&anchor - a) != 12) { print_testfail(); return; }

    print_testpass();
}