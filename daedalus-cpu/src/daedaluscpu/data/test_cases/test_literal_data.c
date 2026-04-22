#include "test_helper.h"

void main()
{
    int i;
    char *s, c;

    i = 10l;
    
    ASSERT(i == 10);

    s = "Hello!"
        "World!";

    ASSERT(s[0] == 'H');
    ASSERT(s[1] == 'e');
    ASSERT(s[2] == 'l');
    ASSERT(s[3] == 'l');
    ASSERT(s[4] == 'o');
    ASSERT(s[5] == '!');
    ASSERT(s[6] == 'W');
    ASSERT(s[7] == 'o');
    ASSERT(s[8] == 'r');
    ASSERT(s[9] == 'l');
    ASSERT(s[10] == 'd');
    ASSERT(s[11] == '!');
    ASSERT(s[12] == 0);

    c = ' ';
    ASSERT(c == ' ');
    
    s = &"bla"[2]; // This is fine!
    ASSERT(*s == 'a');
    ASSERT(s[1] == 0);

    print_testpass();
}