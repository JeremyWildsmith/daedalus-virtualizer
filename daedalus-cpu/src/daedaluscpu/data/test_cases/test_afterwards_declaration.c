#include "test_helper.h"

char a = 2;
extern char a; // this is fine too!
char a;        // this is fine

int add(int a, int b);
int add(int a, int b); // fine!
int add(int a, int b)
{
    return a + b;
}
int add(int a, int b); // fine!

void main() {
    ASSERT(a + add(10, 1) == 13)

    print_testpass();
}