#ifndef __FIRMWARE__
#define __FIRMWARE__

#include <stdint.h>

int firmware_read(uint8_t* dest);
void firmware_write(uint8_t data);

#endif