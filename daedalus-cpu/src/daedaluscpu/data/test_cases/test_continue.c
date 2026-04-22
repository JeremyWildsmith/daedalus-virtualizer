#include "test_helper.h"

void main()
{
    int i = 0;
    while (1)
    {
        print_str("Loop header.\n");
        i++;
        if(i < 10)
            continue;
        
        print_str("Terminal\n");
        break;
    }

    print_testpass();
}