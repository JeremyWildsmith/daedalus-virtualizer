#include "test_helper.h"

int main()
{
    int i;
    for (i = 0; i < 10; i++)
    {
        print_hex(i, 8);
        print_str("\n");
    }

    for (i = 0;;)
    {
        if(i > 200) {
            print_str("BREAKING\n");
            break;
        }

        print_hex(i, 8);
        print_str("\n");
        i += 5;
    }

    for (;;)
    {
        if(i > 400) {
            print_str("BREAKING2\n");
            break;
        }
        i += 30;
    }

    for (int x = 300; x < 315; x++)
    {
        print_hex(x, 8);
        print_str("\n");
    }

    print_testpass();
}