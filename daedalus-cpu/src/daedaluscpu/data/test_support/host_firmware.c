#include "firmware.h"
#include <stdio.h>

int firmware_read(uint8_t* dest) {
    return 0;
}

void firmware_write(uint8_t data) {
    printf("%c", data);
}