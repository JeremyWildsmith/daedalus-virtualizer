#include "test_helper.h"

int data[] = {
    10, 20, 30, 40, 50, 60, 70, 80, 90, 100
};

void main(void) {
    int* a = &data[0];
    int b, c;
    b = a[0];
    c = a[3];

    if (b + c != (10 + 40)) {
        print_dec(b + c);
        print_testfail();
        return;
    }

    print_testpass();
}
