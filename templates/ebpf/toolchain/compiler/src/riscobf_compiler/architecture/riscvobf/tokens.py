from ppci.arch.token import Token, bit, bit_concat, bit_range


class RiscObfToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0, 7)
    rd = bit_range(7, 12)
    funct3 = bit_range(12, 15)
    rs1 = bit_range(15, 20)
    rs2 = bit_range(20, 25)
    funct7 = bit_range(25, 32)


class RiscObfIToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0, 7)
    rd = bit_range(7, 12)
    funct3 = bit_range(12, 15)
    rs1 = bit_range(15, 20)
    imm = bit_range(20, 32)


class RiscObfSToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0, 7)
    funct3 = bit_range(12, 15)
    rs1 = bit_range(15, 20)
    rs2 = bit_range(20, 25)
    imm = bit_concat(bit_range(25, 32), bit_range(7, 12))


class RiscObfSBToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0, 7)
    funct3 = bit_range(12, 15)
    rs1 = bit_range(15, 20)
    rs2 = bit_range(20, 25)
    imm = bit(31) + bit(7) + bit_range(25, 31) + bit_range(8, 12)


class RiscObfJToken(Token):
    class Info:
        size = 32

    opcode    = bit_range(0, 7)
    rd        = bit_range(7, 12)

    imm19_12  = bit_range(12, 20)
    imm11     = bit_range(20, 21)
    imm10_1   = bit_range(21, 31)
    imm20     = bit_range(31, 32)

class RiscObfUToken(Token):
    class Info:
        size = 32

    opcode = bit_range(0, 7)
    rd     = bit_range(7, 12)
    imm20  = bit_range(12, 32)
