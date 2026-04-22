import struct

BPF_LD_IMM64 = 0x18
BPF_EXIT     = 0x95
BPF_JA       = 0x05
BPF_CALL     = 0x85

BPF_CLASS_MASK = 0x07
BPF_JMP   = 0x05

INSN_SIZE = 8

def build_key(seed):
    k = (seed * 1732714 + 1182730741) & 0xffffffff
    return k

def encrypt_instr(seed, addr, data):
    k = build_key(seed & 0xffffffff)

    w0, w1 = struct.unpack('<II', data[addr:addr+8])
    
    k0 = k
    k1 = (k >> 16) ^ k

    w0 ^= k0
    w1 ^= k1

    encrypted = struct.pack('<II', w0, w1)

    data[addr:addr+8] = encrypted

    return data

def remap_opcodes(code_bytes, opcode_mapping, *, encrypt_seed=None, start=0):
    visited = set()
    queue = [start]

    remapped_code = bytearray(code_bytes)

    while queue:
        addr = queue.pop(0)
        
        if addr in visited:
            continue

        while True:
            opcode, regs, offset, imm = struct.unpack(
                '<BBhi', code_bytes[addr:addr+8]
            )
            
            if addr not in visited:
                visited.add(addr)
                remapped_code[addr] = opcode_mapping[opcode]
                if encrypt_seed:
                    encrypt_instr(encrypt_seed + addr, addr, remapped_code)
                    
                    if opcode == BPF_LD_IMM64:
                        encrypt_instr(encrypt_seed + addr, addr + INSN_SIZE, remapped_code)
                        
            if opcode == BPF_LD_IMM64:
                addr += 2 * INSN_SIZE
                continue

            if opcode == BPF_EXIT:
                break

            if opcode == BPF_CALL:
                target = addr + INSN_SIZE + (imm * INSN_SIZE)
                queue.append(target)

                addr += INSN_SIZE
                continue

            if opcode & BPF_CLASS_MASK == BPF_JMP:
                target = addr + INSN_SIZE + (offset * INSN_SIZE)
                queue.append(target)

                if opcode != BPF_JA:
                    fallthrough = addr + INSN_SIZE
                    queue.append(fallthrough)

                break

            addr += INSN_SIZE

    return remapped_code