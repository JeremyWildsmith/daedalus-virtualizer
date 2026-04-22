
from dataclasses import dataclass
import struct

@dataclass(frozen=True)
class FunctionRange:
    symbol_name: str
    section_name: str
    start_offset: int
    size: int

    @property
    def end_offset(self) -> int:
        return self.start_offset + self.size


def get_function_symbols(linked_obj):
    result = []
    for sym in linked_obj.symbols:
        if not getattr(sym, "defined", False):
            continue
        if not getattr(sym, "is_function", False):
            continue
        if sym.section is None:
            continue
        if sym.section.lower() not in {"code", ".text", "text", "CODE"}:
            continue
        result.append(sym)
    return result


def _function_ranges_from_symbols(linked_obj):
    funcs = get_function_symbols(linked_obj)
    by_section = {}
    for sym in funcs:
        by_section.setdefault(sym.section, []).append(sym)

    ranges = []

    for section_name, symbols in by_section.items():
        section = linked_obj.get_section(section_name)
        symbols.sort(key=lambda s: s.value)

        for i, sym in enumerate(symbols):
            start = int(sym.value)

            if getattr(sym, "size", 0):
                size = int(sym.size)
            elif i + 1 < len(symbols):
                size = int(symbols[i + 1].value) - start
            else:
                size = section.size - start

            end = start + size
            if end > section.size:
                size = max(0, section.size - start)

            ranges.append(
                FunctionRange(
                    symbol_name=sym.name,
                    section_name=section_name,
                    start_offset=start,
                    size=size,
                )
            )

    ranges.sort(key=lambda r: (r.section_name, r.start_offset, r.symbol_name))

    return ranges

def build_key(seed):
    k = (seed * 1732714 + 1182730741) & 0xffffffff
    return k

def encrypt_instr(seed, addr, data):
    k = build_key(seed & 0xffffffff)

    (w0,) = struct.unpack('<I', data[addr:addr+4])

    w0 ^= k

    encrypted = struct.pack('<I', w0)

    data[addr:addr+4] = encrypted

    return data

def instruction_encrypt_link_result(linked_obj, seed):
    for f in _function_ranges_from_symbols(linked_obj):
        section = linked_obj.get_section(f.section_name)
        base_address = section.address
        
        data = bytearray(section.data) #[f.start_offset:f.end_offset])
        data_length = f.end_offset - f.start_offset
        
        if data_length % 4 != 0:
            raise Exception("Invalid number of bytes.")
        
        for i in range(int(data_length / 4)):
            relative_addr = f.start_offset + i * 4
            real_addr = base_address + relative_addr
            encrypt_instr(seed + real_addr, relative_addr, data)
    
        section.data = bytes(data)
    
    return linked_obj


def memory_encrypt_file(input_path, ram_encrypt_seed):
    with open(input_path, "rb") as f:
        plain_data = f.read()

    # Pad data, since we encrypt on units of HDL ram memory cells, which is 32 bits.
    remainder = len(plain_data) % 4
    if remainder:
        padding = 4 - remainder
        plain_data += b'\x00' * padding

    encrypted_data = bytearray()

    for idx in range(len(plain_data) // 4):
        plain_dword = struct.unpack("<I", plain_data[idx*4:idx*4+4])[0]

        key = (ram_encrypt_seed + idx) & 0xFFFFFFFF
        key = (key * 1732714) & 0xFFFFFFFF
        key = (key + 1182730741) & 0xFFFFFFFF

        encrypted_word = plain_dword ^ key

        encrypted_data += struct.pack("<I", encrypted_word)

    with open(input_path, "wb") as f:
        f.write(encrypted_data)
