#include "test_helper.h"

int test(int d, int i, int c) {
    c = (((d < 10) || (i != c)) | 22) != 0;
    return c;
}

void main()
{
    print_hex(test(1, 5, 5), 8);
    print_hex(test(100, 5, 5), 8);
    print_hex(test(100, 4, 5), 8);

    print_testpass();
}