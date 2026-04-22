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

void main() {
    char buffer[256];
	print_str("This is an echo service. Write something and I'll write it back to you :)\n");

	for(;;) {
		read_str(buffer, sizeof(buffer), '\n');
		print_str("From the Virtual CPU, you entered: ");
		print_str((char*)buffer);
		print_str("\n");
	}
}