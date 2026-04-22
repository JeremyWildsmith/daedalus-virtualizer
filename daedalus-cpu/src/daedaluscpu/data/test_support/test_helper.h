#include "firmware.h"

#define ASSERT(c) if(!(c)) {print_testfail(); return;}

static void print_chr(char ch)
{
	firmware_write(ch);
}

static void print_str(const char *p)
{
	while (*p != 0)
		firmware_write(*(p++));
}

static void print_dec(unsigned int val)
{
	char buffer[10];
	char *p = buffer;
	while (val || p == buffer) {
		*(p++) = val % 10;
		val = val / 10;
	}
	while (p != buffer) {
		firmware_write('0' + *(--p));
	}
}

static void print_hex(unsigned int val, int digits)
{
	for (int i = (4*digits)-4; i >= 0; i -= 4)
		firmware_write("0123456789ABCDEF"[(val >> i) % 16]);
}

static void print_testpass()
{
	print_str("\nTEST_PASS\n");
	print_str("!!!TEST_END!!!\n");
}

static void print_testfail()
{
	print_str("\nTEST_FAIL\n");
	print_str("!!!TEST_END!!!\n");
}
