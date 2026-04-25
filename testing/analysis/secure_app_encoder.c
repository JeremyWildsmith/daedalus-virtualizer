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
    char encoded[256];

	for(;;) {
	    print_str("Enter a string to encode: \n");
        
		read_str(buffer, sizeof(buffer), '\n');
        for(int i = 0; i < sizeof(buffer); i++) {
            if(buffer[i] == 0) {
                encoded[i] = 0;
                break;
            }
            encoded[i] = buffer[i] + 1;
        }
	    print_str("Press Enter to get the encoded results.\n");
		read_str(buffer, sizeof(buffer), '\n');
		print_str("Your encoded text: ");
		print_str((char*)encoded);
		print_str("\n");
	}
}