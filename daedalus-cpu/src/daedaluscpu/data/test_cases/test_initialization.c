#include "test_helper.h"

struct rec
{
    int a, b;
    char c[5];
    struct
    {
        int x, y;
    } d;
};

char x = '\2';
int *ptr = (int *)0x1000;
int data;
int *ptr2 = &data;

struct rec d = {
    .a = 0,
    .b = 2,
    .c = {0, 0, 3, 0, 0},
    .d = {.x = 100, .y = 0}
};

int e[] = {2, 0, 3, 0, 0, 0, 2};
int f[] = {1, 2, [5] = 6};

void main()
{
    ASSERT(x == '\2');
    ASSERT(ptr == (int*)0x1000);
    ASSERT(ptr2 == &data);

    ASSERT(d.a == 0 && d.b == 2);
    ASSERT(d.c[0] == 0 && d.c[2] == 3 && d.c[4] == 0);
    ASSERT(d.d.x == 100 && d.d.y == 0);

    ASSERT(e[0] == 2 && e[1] == 0 && e[2] == 3 && e[6] == 2); /* 2.2 -> 2 */
    ASSERT(f[0] == 1 && f[1] == 2 && f[5] == 6);

    {
        char x = '\2';
        int *ptr = (int *)0x1000;
        struct rec d = {
            .a = 0,
            .b = 2,
            .c = {0, 0, 3, 0, 0},
            .d = {.x = 100, .y = 0}
        };

        int e[] = {2, 0, 3, 0, 0, 0, 2};
        int f[] = {1, 2, [5] = 6};

        ASSERT(x == '\2' && ptr == (int*)0x1000);
        ASSERT(d.a == 0 && d.b == 2 && d.c[2] == 3 && d.d.x == 100 && d.d.y == 0);
        ASSERT(e[0] == 2 && e[2] == 3 && e[6] == 2);
        ASSERT(f[1] == 2 && f[5] == 6);
    }

    print_testpass();
}