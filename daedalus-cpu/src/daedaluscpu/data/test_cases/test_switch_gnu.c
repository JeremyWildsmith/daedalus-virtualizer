#include "test_helper.h"

void main()
{
    int a = 0;
    
    print_str("Start\n");
    while (a >= 0)
    {
        print_str("Loop\n");
        switch (a)
        {
        case 0 ... 1:
            print_str("Case 0\n");
            a++;
            break;
        default:
            print_str("Default Case\n");
            a = -1;
            break;
        }
    }

    print_testpass();
}