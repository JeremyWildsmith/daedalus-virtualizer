#include "test_helper.h"

int a[10];
int b[] = {1, 2};
int bbb[] = {1, 2,}; // Trailing comma

void main(void) {
    int c[sizeof(long int) / sizeof(char)];
    unsigned long d[] = {1UL, 2UL};

    for (unsigned i = 0; i < (unsigned)(sizeof(c) / sizeof(c[0])); i++)
        c[i] = 0;

    a[2] = b[1] + c[2] + (int)d[1];

    int* p = a + 2;
    int A[][3] = {1,2,3,4,5,6,7,8,9};

    ASSERT((sizeof(a) / sizeof(a[0])) == 10u);
    ASSERT((sizeof(b) / sizeof(b[0])) == 2u);
    ASSERT((sizeof(bbb) / sizeof(bbb[0])) == 2u);

    ASSERT(b[0] == 1 && b[1] == 2);
    ASSERT(bbb[0] == 1 && bbb[1] == 2);

    ASSERT((sizeof(c) / sizeof(c[0])) == (sizeof(long int) / sizeof(char)));
    ASSERT(d[0] == 1UL && d[1] == 2UL);

    ASSERT(p == &a[2]);
    ASSERT(*p == 4);
    ASSERT(a[2] == 4);

    ASSERT(A[0][0] == 1 && A[0][2] == 3);
    ASSERT(A[1][0] == 4 && A[1][2] == 6);
    ASSERT(A[2][0] == 7 && A[2][2] == 9);

    print_testpass();
}
