#include "test_helper.h"

int *pa1 = (int[]){1, 2, 3, 4};
int *pa2 = (int[4]){1, 2, 3, 4};
struct S2
{
    int a;
};
struct S2 *ps1 = &((struct S2){.a = 2});
struct S2 *ps2 = &((struct S2){});

void main(void) {

    /* Initial array contents */
    ASSERT(pa1[0] == 1); ASSERT(pa1[1] == 2); ASSERT(pa1[2] == 3); ASSERT(pa1[3] == 4);
    ASSERT(pa2[0] == 1); ASSERT(pa2[1] == 2); ASSERT(pa2[2] == 3); ASSERT(pa2[3] == 4);

    /* They should be different arrays (different objects) */
    ASSERT(pa1 != pa2);

    pa1[0] = 12;
    ASSERT(pa1[0] == 12);
    ASSERT(pa2[0] == 1);

    pa2[3] = 13;
    ASSERT(pa2[3] == 13);
    ASSERT(pa1[3] == 4);

    ASSERT(ps1->a == 2);
    ASSERT(ps2->a == 0);

    ps2->a = 14;
    ASSERT(ps2->a == 14);
    ASSERT(ps1->a == 2);

    print_testpass();

}
