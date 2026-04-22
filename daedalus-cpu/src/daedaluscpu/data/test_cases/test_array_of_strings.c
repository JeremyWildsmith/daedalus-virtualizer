#include "test_helper.h"

char *msg[] = {
    "Hi",
    "Bonjour"};

void main()
{
    // This test is effective by virtue of compating host and secure enclave output.

    print_str(msg[0]);
    print_str(":::\n");
    print_str(msg[1]);

    print_testpass();
}