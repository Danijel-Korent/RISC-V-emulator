# RISC-V-emulator
A small exercise to learn the RISC-V instruction set. The end goal was to boot an MMU-less version of the Linux Kernel, which is achieved now.

I'm writing it to explore the "problem space", i.e. to understand the RISC-V architecture. I also plan to use it to learn Rust. After I finish the project in Python, I will rewrite it in Rust.

I'm also writing a blog post about each implemented instruction, and will put links here when the blog is ready (UPDATE: this turned out to be a lie so far :) )

## Running the emulator

`python3 main.py`

## Current status

The emulator successfully loads the kernel image and device tree binary, and boots Linux into the Busybox's Ash shell. It executes around 63 million instructions to reach the shell prompt. It supports most instructions of the rv32ima instruction set 
(only implemented what is needed to boot the kernel and run ls/cat)

Currently, input only works when running on Windows. On Linux, the emulator stops after the shell prompt gets output (currently working on Linux input support that doesn't require an external Python library)

The emulator can also print which kernel function the CPU is currently executing by comparing the current PC with entries in a .map file

You may think that the emulator is unreasonably slow, but if you take a look at that code, you will see that it is quite reasonable to be this slow. There are around 10 function calls per single instruction, which is a death on Python for a program of this type. But this is how I wanted to write it. If I put most of this function into a single big loop, it will probably be 5-10x faster. I will try it when I have time for it. So far, I spent some 20 min to disable logging function calls and execute multiple instructions (1000x) before updating peripherals, and that yielded 50% increase (didn't commit it)

**TODO:**
  * I will try to add input handling on Linux without using external libraries 
    * I have mistakenly thought that "termios" is an external module, but it looks like it is part of the standard library
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
    

## Running the Linux kernel image in QEMU

`qemu-system-riscv32 -machine virt -nographic -bios none -kernel Linux_kernel_image/Linux_image_6_1_14_RV32IMA_NoMMU`

(No need to provide dtb as "virt" machine constructs its own dtb blob and gives it to kernel)

## Screenshot
![RISC-V Emulator](/emulator_screenshot.png?raw=true "RISC-V Emulator")
