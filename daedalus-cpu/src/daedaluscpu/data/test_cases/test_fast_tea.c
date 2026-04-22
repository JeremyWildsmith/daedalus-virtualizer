// Test TEA Encryption ALgoirthm in Enclave
// Sourced from https://en.wikipedia.org/wiki/Tiny_Encryption_Algorithm

#include "test_helper.h"

// Just use random data for testing

uint8_t payload[16] = {
    0x9b, 0x3c, 0x39, 0x78, 0xc8, 0xc5, 0xaf, 0x6a, 0x10, 0xd4, 0x50, 0xa4, 0x12, 0x61, 0xf1, 0x90};

uint32_t key[4] = {0xcdb4f28d, 0x8458c7aa, 0x39571135, 0xf7ba4deb};

void encrypt(uint32_t v[2], const uint32_t k[4])
{
    uint32_t v0 = v[0], v1 = v[1], sum = 0, i;
    uint32_t delta = 0x9E3779B9;
    uint32_t k0 = k[0], k1 = k[1], k2 = k[2], k3 = k[3];
    for (i = 0; i < 32; i++)
    {
        print_hex(sum, 8);
        print_chr('\n');
        sum += delta;
        v0 += ((v1 << 4) + k0) ^ (v1 + sum) ^ ((v1 >> 5) + k1);
        v1 += ((v0 << 4) + k2) ^ (v0 + sum) ^ ((v0 >> 5) + k3);
    }
    v[0] = v0;
    v[1] = v1;
}

void main()
{
    if(sizeof(payload) % (sizeof(uint32_t) * 2) != 0) {
        print_testfail();
        return;
    }

    int block_size = (sizeof(uint32_t) * 2);

    //We apply 1 encrypt iterations
    for(int b = 0; b < sizeof(payload); b += block_size) {
        print_str("Start block crypt\n");
        print_dec(b / block_size);
        print_str("\n");
        
        uint32_t* pblock = (uint32_t*)(&payload[b]);
        encrypt(pblock, key);
    }

    print_str("Encrypted Payload: ");
    //We print it out, this will secure the output from host to enclave to ensure it is consistent.
    for(int i = 0; i < sizeof(payload); i++) {
        print_hex(payload[i], 2);
    }

    print_str("\n");
    print_testpass();
}