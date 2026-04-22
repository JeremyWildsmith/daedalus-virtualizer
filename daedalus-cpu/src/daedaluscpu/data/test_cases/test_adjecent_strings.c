#include "test_helper.h"

void main(int b)
{
    print_str("Hello"
           "world\n");
    static unsigned char msg[] = "Woooot\n";
    print_str(msg);
    print_testpass();
}