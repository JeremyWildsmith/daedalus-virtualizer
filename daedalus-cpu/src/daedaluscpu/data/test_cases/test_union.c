#include "test_helper.h"

union z { int foo; struct { int b, a, r; } bar;};
union z myZ[2] = {1, 2};

void main() {
    union z localZ = {0};
    myZ[0].foo == 1;

    ASSERT(myZ[0].foo == 1);

    union z struct_test = {0};
    struct_test.bar.b = 10;
    struct_test.bar.a = 20;
    struct_test.bar.r = 30;

    ASSERT(struct_test.bar.b == 10);
    ASSERT(struct_test.bar.a == 20);
    ASSERT(struct_test.bar.r == 30);

    print_testpass();
}
