// Test fnv hash: https://en.wikipedia.org/wiki/Fowler%E2%80%93Noll%E2%80%93Vo_hash_function

#include "test_helper.h"

static unsigned int string_length(const char* s) {
    unsigned int i = 0;

    for(i; s[i]; i++) {}

    return i;
}

static unsigned int fnvHash(const char* str)
{
    const unsigned int length = string_length(str) + 1;
    unsigned int hash = 2166136261;
    for (unsigned int i = 0; i < length; ++i)
    {
        hash ^= *str++;
        hash *= 16777619;
    }
    return hash & 0xFFFFFFFF;
}

void main() {
    //The test is accomplished by comparing output from host and enclave.
    print_hex(fnvHash("hello world"), 8);
    print_str("\n");
    print_testpass();
}