#include "test_helper.h"

int f(int a)
{
    print_str("f was called\n");
    if (a == 0) {    
        print_str("f is returning with a value\n");
        return (1);
    }
    
    print_str("f is returning with no explicit return value\n");
}

void main() {
    print_str("Calling f\n");
    ASSERT(f(0) == 1);
    print_str("f returned control flow\n");
    print_testpass();
}