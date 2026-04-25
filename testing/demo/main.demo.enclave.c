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

void print_str(const char *p)
{
	while (*p != 0)
		firmware_write(*(p++));
}

unsigned long build_key(char* key) {
    unsigned long hash = 5381;
    int c;

    while ((c = *key++)) {
        hash = ((hash << 5) + hash) + c;
    }

    return hash;
}

//We source this from: https://en.wikipedia.org/wiki/Linear_congruential_generator
unsigned int lcg_step(unsigned int current) {
    return current * 1664525u + 1013904223u;
}

//For "Jeremy Wildsmith" the key should be: 8p63qr85-mdo7m7s7-g705q34b-q54vs76h
int compare_key(char* key, unsigned long key_hash) {
    int ki = 0;

    if(!key[ki])
        return 0;

    for(int w = 0;; w++) {
        for(int i = 0; i < 8; i++) {
            if(!key[ki])
                return 0;

            int lower = key_hash % 3 ? 48 : 97;
            int upper_r = key_hash % 3 ? 57 : 122;
            
            char d = lower + (key_hash % (upper_r - lower + 1));

            if(key[ki++] != d)
                return 0;

            key_hash = lcg_step(key_hash);
        }

        if(w < 3) {
            if(key[ki++] != '-')
                return 0;
        } else {
            break;
        }
    }
    
    if(key[ki])
        return 0;

    return 1;
}

void main() {
    char name[256];
    char key[256];
	
	for(;;) {
	    read_str(name, sizeof(name), '\n');
	    read_str(key, sizeof(key), '\n');
        unsigned long hash = build_key(name);

        //To prevent bruteforcing, lets add a busy loop.
        for(int i = 0; i < 1000; i++) {
            name[i % 10] = name[(i + 1) % 10] * name[(i + 2) % 10];
        }

	    if(compare_key(key, hash))
            print_str("VALID\n");
        else
            print_str("NOT_VALID\n");
	}
}
