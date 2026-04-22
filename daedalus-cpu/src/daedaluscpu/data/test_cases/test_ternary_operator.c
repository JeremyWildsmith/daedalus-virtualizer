//NOTE! PPCI's Optimizer breaks this code. If it is failing, reduce optimize level to 0

#include "test_helper.h"

int foo(int x) { return x + 1; }
int bar(int x) { return x - 1; }


void p1(int x) {
    print_str("p1 was called\n");
}

void p2(int x) {
    print_str("p2 was called\n");
}

void test(int b)
{
    int a;
    
    a = b ? foo(22) : bar(22);
    print_hex(a, 8);
    print_str("\n");


    (b ? p1(33) : p2(33));
}

void main() {
    print_str("call 1\n");
    test(0);
    print_str("call 2\n");
    test(1);
    print_testpass();
}