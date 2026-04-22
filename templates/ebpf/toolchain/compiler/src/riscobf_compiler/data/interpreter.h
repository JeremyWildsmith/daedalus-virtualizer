#ifndef INTERPRETER_H
#define INTERPRETER_H
#include "type_helper.h"

struct insn {
    u8  op;
    u8  reg;
    s16 off;
    s32 imm;
};

u32 ebpf_exec(u32 base_address, s32 image_size);
#endif