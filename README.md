# RISC-V-emulator
A small exercise to learn the RISC-V instruction set. The end goal was to boot an MMU-less version of the Linux Kernel, which is achieved now.

I'm writing it to explore the "problem space", i.e. to understand the RISC-V architecture. I also plan to use it to learn Rust. After I finish the project in Python, I will rewrite it in Rust.

I'm also writing a blog post about each implemented instruction, and will put links here when the blog is ready (UPDATE: this turned out to be a lie so far :) )

## Running the emulator

`python3 main.py`

## Current status

The emulator successfully loads the kernel image and device tree binary, and boots Linux into the Busybox's Ash shell. It executes around 63 million instructions to reach the shell prompt. Terminal input now works when running on both Windows and Linux. 

Emulated CPU supports most instructions of the rv32ima instruction set. I only implemented what is needed to boot the kernel and run ls/cat; basically just kept implementing instructions until the emulator stopped reporting unknown instructions.

The emulator can also print which kernel function the CPU is currently executing by comparing the current PC with entries in a .map file

You may think that the emulator is unreasonably slow, but if you take a look at that code, you will see that it is quite reasonable to be this slow. There are around 10 function calls per single instruction, which is a death on Python for a program of this type. But this is how I wanted to write it. If I put most of this function into a single big loop, it will probably be 5-10x faster. I will try it when I have time for it. So far, I spent some 20 min to disable logging function calls and execute multiple instructions (1000x) before updating peripherals, and that yielded 50% increase (didn't commit it)

## Technical details

CPU emulates:
  * All RV32I instructions except for "slti"
  * All RV32M instructions except for "mulhsu"
  * All RV32A instructions except for xor, max, min
  * All Zicsr instructions
  * Interrupts and ecall/ebreak
  * CSR registers for flags, interrupts, privilege, and Xen console
  * Privilege levels are only emulated at the interface level; Didn't add code for checking if an instruction is allowed to be executed

Devices:
  * CLINT -> implements "mtime" and "mtimeCmp". Software interrupts not implemented
  * UART -> It only implements bare minimum: registers RBR, THR and LSR
  * RAM -> only 64M as RAM is currently expensive ;)
  * Xen hvc0 console via CSR registers

CPU address space:
```
    10000000-10000008 : UART
    11000000-1100BFFF : CLINT
    80000000-84000000 : RAM
```

Other:
  * No MMU support
  * Supports Linux boot protocol for RISC-V
    
## Special Thanks

  * To @cnlohr and his [mini-rv32ima emulator](https://github.com/cnlohr/mini-rv32ima). Had used his project to:
    * to generate mmu-less rv32 Linux image
    * to debug/trace where CPU execution started to deviate by tracing differences in CPU state between my emulator and mini-rv32ima. Saved me a huge amount of time!
  * @d0iasm and section ["Control and Status Registers"](https://book.rvemu.app/hardware-components/03-csrs.html) in her book that very nicely summarizes important CSR registers 
  * [rvcodecjs](https://luplab.gitlab.io/rvcodecjs/) for checking opcodes of unimplemented instructions
  * This [instruction cheat sheet](https://www.cs.sfu.ca/~ashriram/Courses/CS295/assets/notebooks/RISCV/RISCV_CARD.pdf) was very helpful!



## Running the Linux kernel image in QEMU

`qemu-system-riscv32 -machine virt -nographic -bios none -kernel Linux_kernel_image/Linux_image_6_1_14_RV32IMA_NoMMU`

(No need to provide dtb as "virt" machine constructs its own dtb blob and gives it to kernel)

## Screenshot
![RISC-V Emulator](/emulator_screenshot.png?raw=true "RISC-V Emulator")
