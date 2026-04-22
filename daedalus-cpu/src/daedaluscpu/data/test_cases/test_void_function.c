#include "test_helper.h"

void other(void) {
    print_str("Other function was called.");
}

void main(void)
{
    // The print statements are effective at testing the calling semantics
    // because the output is compared to execution on the host platform (outside of virtual enclave)
    print_str("Calling other function.");
    other();
    print_str("Returned from other function.");

    print_testpass();
}