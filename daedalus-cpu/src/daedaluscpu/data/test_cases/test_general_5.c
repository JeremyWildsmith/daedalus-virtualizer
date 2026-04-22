#include "test_helper.h"

static int G;

void initialize(int g)
{
    G = g;
}

void main()
{
    int d = 2;
    initialize(d);
    ASSERT(G == 2);
    print_testpass();
}