SECTIONS
{
  . = 0;

  .text : ALIGN(8) {
    KEEP(*(.text.main))
    *(.text .text.*)
  }

  .rodata : ALIGN(8) {
    *(.rodata .rodata.*)
    *(.rodata.str1.*)
  }

  .data : ALIGN(8) {
    *(.data .data.*)
    *(.sdata .sdata.*)

    /* Keep uninitialized data, basically, it simplifies work for the interpreter (knows how to map addresses.)*/
    *(.bss .bss.*)
    *(.sbss .sbss.*)
    *(COMMON)
  }

  /DISCARD/ : {
    *(.comment)
    *(.eh_frame)
    *(.note*)
    *(.llvm_addrsig)
    *(.strtab)
    *(.symtab)
  }
}