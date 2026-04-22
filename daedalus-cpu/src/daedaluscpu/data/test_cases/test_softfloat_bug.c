#include "test_helper.h"

#define INLINE
typedef short int16;
typedef unsigned int bits32;
typedef char int8;

struct shift64_extra_result {
    bits32 z0;
    bits32 z1;
    bits32 z2;
};

INLINE void
shift64ExtraRightJamming(
    bits32 a0,
    bits32 a1,
    bits32 a2,
    int16 count,
    struct shift64_extra_result* b)
{
    bits32 z0, z1, z2;
    int8 negCount = (-count) & 31;

    if (count == 0)
    {
        z2 = a2;
        z1 = a1;
        z0 = a0;
    }
    else
    {
        if (count < 32)
        {
            z2 = a1 << negCount;
            z1 = (a0 << negCount) | (a1 >> count);
            z0 = a0 >> count;
        }
        else
        {
            if (count == 32)
            {
                z2 = a1;
                z1 = a0;
            }
            else
            {
                a2 |= a1;
                if (count < 64)
                {
                    z2 = a0 << negCount;
                    z1 = a0 >> (count & 31);
                }
                else
                {
                    z2 = (count == 64) ? a0 : (a0 != 0);
                    z1 = 0;
                }
            }
            z0 = 0;
        }
        z2 |= (a2 != 0);
    }
    b->z2 = z2;
    b->z1 = z1;
    b->z0 = z0;
}

void main(void)
{
    struct shift64_extra_result r;

    // These are basically just fuzz tests to ensure it behaves the same on host and enclave (by virtue of comparing output.)
    // It isn't comprehensive, but offers at least some test coverage.
    shift64ExtraRightJamming(1, 2, 3, 0, &r);
    print_hex(r.z0, 8);
    print_str("\n");
    print_hex(r.z1, 8);
    print_str("\n");
    print_hex(r.z2, 8);
    print_str("\n");

    shift64ExtraRightJamming(12345, 1, 0, 1, &r);
    print_hex(r.z0, 8);
    print_str("\n");
    print_hex(r.z1, 8);
    print_str("\n");
    print_hex(r.z2, 8);
    print_str("\n");

    shift64ExtraRightJamming(555333, 222, 1, 16, &r);
    print_hex(r.z0, 8);
    print_str("\n");
    print_hex(r.z1, 8);
    print_str("\n");
    print_hex(r.z2, 8);
    print_str("\n");

    print_testpass();
}