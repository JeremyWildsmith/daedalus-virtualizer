#include "test_helper.h"

extern int i4; // keep internal linkage
int i4;

void main() {
    i4 = 10;
    ASSERT(i4 == 10);
    print_testpass();
}