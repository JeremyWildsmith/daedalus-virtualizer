#include "test_helper.h"

void main()
{
    int i = 0;
    print_str("Start\n");
    goto part2;
    print_str("This shouldn't execute.\n");
part2:
    print_str("In part2 loop.\n");
    i++;

    if(i > 10)
        goto part3;
    goto part2;

part3:
    print_str("Entered part3\n");
    switch (0)
    {
    case 34:
        break;
    default:
        print_str("Executed default case.\n");
        break;
    }

    print_testpass();
}