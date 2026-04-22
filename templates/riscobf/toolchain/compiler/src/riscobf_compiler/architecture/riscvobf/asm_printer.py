from ppci.arch.asm_printer import AsmPrinter
from ppci.arch.generic_instructions import SectionInstruction


class RiscObfAsmPrinter(AsmPrinter):
    """Riscv specific assembly printer"""

    def print_instruction(self, instruction):
        if isinstance(instruction, SectionInstruction):
            return f".section {instruction.name}"
        else:
            return str(instruction)
