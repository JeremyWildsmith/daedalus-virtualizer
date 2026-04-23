// Test fnv hash: https://en.wikipedia.org/wiki/Fowler%E2%80%93Noll%E2%80%93Vo_hash_function

#include "test_helper.h"
#include "firmware.h"


void read_str(unsigned char* buf, int max_read, unsigned char stopchar)
{
    int i;
    for(i = 0; i < max_read - 1; i++) {
        while(!firmware_read(&buf[i]))
            continue;
        
        if(!buf[i] || buf[i] == stopchar)
            break;
    }

    buf[i] = 0;
}

static unsigned int string_length(const char* s) {
    unsigned int i = 0;

    for(i; s[i]; i++) {}

    return i;
}

static unsigned int fnvHash(const char* str)
{
    const unsigned int length = string_length(str);
    unsigned int hash = 2166136261;
    for (unsigned int i = 0; i < length; ++i)
    {
        hash ^= *str++;
        hash *= 16777619;
    }
    return hash & 0xFFFFFFFF;
}

void main() {
    char buffer[512];
    
    for(;;) {
        read_str(buffer, 512, 0);
        
        if(buffer[0] == 0) {
            continue;
        }

        print_str("!");
        print_hex(fnvHash(buffer), 8);
        print_str("!\n");
    }

    print_testpass();
}