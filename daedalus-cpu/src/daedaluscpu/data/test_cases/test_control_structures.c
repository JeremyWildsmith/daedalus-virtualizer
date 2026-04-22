#include "test_helper.h"

void test_func(int x)
{
    int d, i, c;
    c = 2;
    i = 0xFBEC;
    d = (20 + c * 10 + c >> 2) - 123;
    print_hex(d, 8);
    print_str("\n");
    if (d < 10)
    {
        while (d < 20)
        {
            d = d + c * 4;
        }
        print_hex(d, 8);
        print_str("\n");
    }
    
    d -= x;

    if (d > 20)
    {
        print_str("PRIMARY_CLAUSE\n");
        do
        {
            d += c;
        } while (d < 100);
    }
    else
    {
        print_str("ELSE_CLAUSE\n");
        print_hex(i, 8);
        print_str("\n");
        
        int next = i + 10;
        for (i = i; i < next; i++)
        {
            print_str("ITER\n");
        }
        for (i = 0;;)
        {
            i++;
            if(i > 15)
                break;
        }
        for (;;)
        {
            i += 2;
            break;
        }
        print_hex(i, 8);
        print_str("\n");
    }
}

void main() {
    print_str("FIRST_CALL\n");
    test_func(0);
    print_str("SECOND_CALL\n");
    test_func(200);
    print_testpass();
}