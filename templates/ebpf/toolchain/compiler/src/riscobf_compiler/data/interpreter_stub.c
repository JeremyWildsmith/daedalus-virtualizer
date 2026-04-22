#include "interpreter.h"

extern const unsigned char ebpf_firmware_bin[];
extern unsigned int ebpf_firmware_bin_len;

void main() {
    ebpf_exec((u32)ebpf_firmware_bin, ebpf_firmware_bin_len);
    return;
}
