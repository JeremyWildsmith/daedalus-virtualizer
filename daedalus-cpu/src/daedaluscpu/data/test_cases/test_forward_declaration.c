#include "test_helper.h"

extern char a;

void main() {
    ASSERT(a == 2);
    print_testpass();
}

char a = 2;