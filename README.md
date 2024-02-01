# RISC-V-emulator
A small exercise to learn RISC-V instruction set. The end goal is to boot an MMU-less version of the Linux Kernel.

I'm writing it in Python to explore the "problem space" i.e. understand the RISC-V platform. After I Finish the project in Python, I will use it to learn Rust by rewriting this project in Rust. So in the end there will be two versions of the emulator - one written in Python and the other in Rust

I'm also writing a blog post about each implemented instruction, and will put links here when the blog is ready.

## Current status

The emulator successfully loads the kernel and device tree from the OS image, boots the Linux kernel, executes it up to the start of PID 1, and executes user-space code up to until the first syscall (for the curious: it's ioctl). I'm currently working on fully implementing the instruction "ecall" and privilege mechanics of the RISC-V CPU.

## Running the emulator

`cd RISC-V-emulator/python/`

`python3 main.py`

## Screenshot
![RISC-V Emulator](/emulator_screenshot.png?raw=true "RISC-V Emulator")
