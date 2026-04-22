#include "test_helper.h"

int generate_number(void)
{
    #ifdef HOST_EXEC
        return 123;
    #else
    asm(
        "li a0, 123\n"
        "jalr x0, x1, 0\n"
    );
    #endif
    for(;;) {}
}

void main(void)
{
    ASSERT(generate_number() == 123);
    print_testpass();
}
