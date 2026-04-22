from ppci.utils.bitfun import BitView, wrap_negative
from ppci.arch.encoding import Relocation
from .tokens import RiscObfIToken, RiscObfSBToken, RiscObfToken, RiscObfJToken, RiscObfUToken


class BImm12Relocation(Relocation):
    name = "b_imm12"
    token = RiscObfSBToken
    field = "imm"

    def calc(self, sym_value, reloc_value):
        assert sym_value % 2 == 0
        assert reloc_value % 2 == 0
        offset = (sym_value - reloc_value) // 2
        return wrap_negative(offset, 12)

    def apply(self, sym_value, data, reloc_value):
        """Apply this relocation type given some parameters.

        This is the default implementation which stores the outcome of
        the calculate function into the proper token."""
        assert self.token is not None
        token = self.token.from_data(data)
        assert self.field is not None
        assert hasattr(token, self.field)
        setattr(token, self.field, self.calc(sym_value, reloc_value))
        return token.encode()


class BImm20Relocation(Relocation):
    name = "b_imm20"
    token = RiscObfJToken

    def apply(self, sym_value, data, reloc_value):
        tok = self.token.from_data(data)

        assert sym_value % 2 == 0
        assert reloc_value % 2 == 0

        offset = sym_value - reloc_value

        rel20 = wrap_negative(offset >> 1, 20)

        tok.imm10_1  = (rel20 >> 0)  & 0x3FF
        tok.imm11    = (rel20 >> 10) & 0x1
        tok.imm19_12 = (rel20 >> 11) & 0xFF
        tok.imm20    = (rel20 >> 19) & 0x1

        return tok.encode()

class Abs32Imm20Relocation(Relocation):
    name = "abs32_imm20"
    token = RiscObfUToken

    def apply(self, sym_value, data, reloc_value):
        tok = self.token.from_data(data)

        assert sym_value % 2 == 0

        hi20 = (sym_value + 0x800) >> 12

        tok.imm20 = hi20 & 0xFFFFF
        return tok.encode()

class RelImm20Relocation(Relocation):
    name = "rel_imm20"
    token = RiscObfUToken

    def apply(self, sym_value, data, reloc_value):
        tok = self.token.from_data(data)

        assert sym_value % 2 == 0
        assert reloc_value % 2 == 0

        offset = sym_value - reloc_value

        hi20 = (offset + 0x800) >> 12

        tok.imm20 = hi20 & 0xFFFFF
        return tok.encode()

class Abs32Imm12Relocation(Relocation):
    name = "abs32_imm12"
    token = RiscObfIToken
    field = "imm"

    def calc(self, sym_value, reloc_value):
        assert sym_value % 2 == 0
        return sym_value & 0xFFF

class RelImm12Relocation(Relocation):
    name = "rel_imm12"
    token = RiscObfIToken
    field = "imm"

    def calc(self, sym_value, reloc_value):
        assert sym_value % 2 == 0
        assert reloc_value % 2 == 0

        offset = sym_value - reloc_value + 4
        return offset & 0xFFF

class AbsAddr32Relocation(Relocation):
    name = "absaddr32"
    token = RiscObfToken

    def apply(self, sym_value, data, reloc_value):
        offset = sym_value
        bv = BitView(data, 0, 4)
        bv[0:32] = offset
        return data
