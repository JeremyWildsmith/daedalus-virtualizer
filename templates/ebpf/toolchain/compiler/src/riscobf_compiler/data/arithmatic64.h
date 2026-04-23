/*
	Helper to support 64bit arithmatic operations on an compilr architecture that does not support
	64 bits types.
*/
#ifndef ARITHMATIC64_
#define ARITHMATIC64_

#define WORD_BITS 32u
#define DWORD_BITS 64u

#include "type_helper.h"

typedef struct {
	u32 lower;
	u32 upper;
} ua64;


static inline ua64 a64_zero(void)
{
    ua64 x;
    x.lower = 0;
    x.upper = 0;
    return x;
}

static inline ua64 a64_from_u32(u32 v)
{
    ua64 x;
    x.lower = v;
    x.upper = 0;
    return x;
}

static inline ua64 a64_from_s32(s32 v)
{
    ua64 x;
    x.lower = (u32)v;
    x.upper = (v < 0) ? 0xffffffffu : 0u;
    return x;
}

static inline int a64_is_zero(ua64 a)
{
    return a.lower == 0 && a.upper == 0;
}

static inline int a64_eq(ua64 a, ua64 b)
{
    return a.lower == b.lower && a.upper == b.upper;
}

static inline int a64_ne(ua64 a, ua64 b)
{
    return !a64_eq(a, b);
}

static inline int a64_gt_u(ua64 a, ua64 b)
{
    if (a.upper != b.upper) return a.upper > b.upper;
    return a.lower > b.lower;
}

static inline int a64_ge_u(ua64 a, ua64 b)
{
    if (a.upper != b.upper) return a.upper > b.upper;
    return a.lower >= b.lower;
}

static inline int a64_lt_s(ua64 a, ua64 b)
{
    s32 ahi = (s32)a.upper;
    s32 bhi = (s32)b.upper;
    if (ahi != bhi) return ahi < bhi;
    return a.lower < b.lower;
}

static inline int a64_le_s(ua64 a, ua64 b)
{
    s32 ahi = (s32)a.upper;
    s32 bhi = (s32)b.upper;
    if (ahi != bhi) return ahi < bhi;
    return a.lower <= b.lower;
}

static inline int a64_gt_s(ua64 a, ua64 b)
{
    s32 ahi = (s32)a.upper;
    s32 bhi = (s32)b.upper;
    if (ahi != bhi) return ahi > bhi;
    return a.lower > b.lower;
}

static inline int a64_ge_s(ua64 a, ua64 b)
{
    s32 ahi = (s32)a.upper;
    s32 bhi = (s32)b.upper;
    if (ahi != bhi) return ahi > bhi;
    return a.lower >= b.lower;
}

static inline ua64 a64_not(ua64 a)
{
    ua64 x;
    x.lower = ~a.lower;
    x.upper = ~a.upper;
    return x;
}

static inline ua64 a64_neg(ua64 a)
{
    ua64 x = a64_not(a);
    u32 old = x.lower;
    x.lower += 1u;
    if (x.lower < old) x.upper += 1u;
    return x;
}

static inline ua64 a64_add(ua64 a, ua64 b)
{
    ua64 x;
    u32 old = a.lower;
    x.lower = a.lower + b.lower;
    x.upper = a.upper + b.upper + ((x.lower < old) ? 1u : 0u);
    return x;
}

static inline ua64 a64_sub(ua64 a, ua64 b)
{
    ua64 x;
    x.lower = a.lower - b.lower;
    x.upper = a.upper - b.upper - ((a.lower < b.lower) ? 1u : 0u);
    return x;
}

static inline ua64 a64_and(ua64 a, ua64 b)
{
    ua64 x;
    x.lower = a.lower & b.lower;
    x.upper = a.upper & b.upper;
    return x;
}

static inline ua64 a64_or(ua64 a, ua64 b)
{
    ua64 x;
    x.lower = a.lower | b.lower;
    x.upper = a.upper | b.upper;
    return x;
}

static inline ua64 a64_xor(ua64 a, ua64 b)
{
    ua64 x;
    x.lower = a.lower ^ b.lower;
    x.upper = a.upper ^ b.upper;
    return x;
}

static inline ua64 a64_set_bit(u32 bit)
{
    ua64 x = a64_zero();
    if (bit < 32u) x.lower = 1u << bit;
    else if (bit < 64u) x.upper = 1u << (bit - 32u);
    return x;
}


// Reimplementation of this algorithim: https://android.googlesource.com/toolchain/compiler-rt/+/release_32/lib/ashldi3.c
static inline ua64 a64_lsh(ua64 a, u32 sh)
{
    sh &= 63;

    ua64 input;
    ua64 result;

    input = a;
    if (sh & WORD_BITS) {
        result.lower = 0;
        result.upper = (sh >= DWORD_BITS) ? 0 : (input.lower << (sh - WORD_BITS));
    }
    else {
        if (sh == 0)
            return a;
        result.lower = input.lower << sh;
        result.upper = (input.upper << sh) | (input.lower >> (WORD_BITS - sh));
    }
    return result;
}

// Reimplementation of this algorithm: https://github.com/torvalds/linux/blob/master/lib/lshrdi3.c
static inline ua64 a64_rsh(ua64 a, u32 sh)
{
    sh &= 63;

    if (sh == 0)
        return a;

    ua64 input;
    ua64 result;

    input = a;
    // Check if it is less than 0 (sign bit is set)
    if (sh & WORD_BITS) {
        result.upper = 0;
        result.lower = (sh >= DWORD_BITS) ? 0 : (input.upper >> (sh - WORD_BITS));
    }
    else {
        result.upper = input.upper >> sh;
        result.lower = (input.upper << (WORD_BITS - sh)) | (input.lower >> sh);
    }
    return result;
}

// Reimplementation of this algorithm for 64 bit shift: https://github.com/llvm-mirror/compiler-rt/blob/master/lib/builtins/ashrdi3.c
static inline ua64 a64_arsh(ua64 a, u32 sh)
{
    //Limit the shift amount, a shift greater than 63 is invalid.
    sh &= 63;

    ua64 input;
    ua64 result;

    input = a;
    if (sh & WORD_BITS) {
        result.upper = ((s32)input.upper < 0) ? -1 : 0u;
        result.lower = (u32)(((s32)input.upper) >> (sh - WORD_BITS));
    }
    else {
        if (sh == 0)
            return a;
        result.upper = (u32)(((s32)input.upper) >> sh);
        result.lower = ((u32)input.upper << (WORD_BITS - sh)) | (input.lower >> sh);
    }
    return result;
}

//Use algorithm: "Restoring division" from https://en.wikipedia.org/wiki/Division_algorithm
static inline void a64_udivmod(ua64 num, ua64 den, ua64* q, ua64* rem)
{
    ua64 quotient = a64_zero();
    ua64 remainder = a64_zero();
    u32 bit;

    if (a64_is_zero(den)) {
        *q = a64_zero();
        *rem = a64_zero();
        return;
    }

    //Basically we just do long division but on binary digits.
    for (bit = 63; bit >= 0; bit--) {
        //Shift left
        remainder = a64_lsh(remainder, 1u);

        // Select either the upper or lower u32 part
        if (bit >= 32u) {
            remainder.lower |= (num.upper >> (bit - 32)) & 1u;
        }
        else {
            remainder.lower |= (num.lower >> bit) & 1;
        }

        if (a64_ge_u(remainder, den)) {
            remainder = a64_sub(remainder, den);
            quotient = a64_or(quotient, a64_set_bit(bit));
        }
    }

    *q = quotient;
    *rem = remainder;
}


// Reimplementation from: https://github.com/hcs0/Hackers-Delight/blob/master/mulmnu.c.txt
static inline ua64 a64_mul(ua64 a, ua64 b)
{
    unsigned short u[4], v[4], w[8];
    ua64 r;
    unsigned int k, t;
    int i, j;

    u[0] = (unsigned short)(a.lower);
    u[1] = (unsigned short)(a.lower >> 16);
    u[2] = (unsigned short)(a.upper);
    u[3] = (unsigned short)(a.upper >> 16);

    v[0] = (unsigned short)(b.lower);
    v[1] = (unsigned short)(b.lower >> 16);
    v[2] = (unsigned short)(b.upper);
    v[3] = (unsigned short)(b.upper >> 16);

    for (i = 0; i < 4; i++)
        w[i] = 0;

    for (j = 0; j < 4; j++) {
        k = 0;
        for (i = 0; i < 4; i++) {
            t = u[i] * v[j] + w[i + j] + k;
            w[i + j] = (unsigned short)t;
            k = t >> 16;
        }
        w[j + 4] = (unsigned short)k;
    }

    r.lower = (u32)w[0] | ((u32)w[1] << 16);
    r.upper = (u32)w[2] | ((u32)w[3] << 16);
    return r;
}

#endif