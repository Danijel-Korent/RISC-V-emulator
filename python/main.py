#! /usr/bin/env python3

# Implementing RISC-V CPU emulator - only RV32IMA instruction set (32-bit integer + multiplication/division + atomics)

from instruction_executer import execute_instruction
from memory import Memory
from registers import Registers

instruction_no_counter = 0


def execute_single_CPU_instruction(registers, memory):
    global instruction_no_counter

    instruction_no_counter += 1

    # Print informational data
    registers.print_register_values()
    print("\n===============================")
    print(f"Instruction no.:     {instruction_no_counter}")
    print("===============================")
    print(f"Instruction pointer: 0x{registers.instruction_pointer:08x}")

    # Fetch
    instruction = memory.get_4_bytes__little_endian(registers.instruction_pointer)

    print(f"Instruction value:   0x{instruction:08x} \n")

    # Execute
    instruction_pointer_updated = execute_instruction(registers, memory, instruction)

    # Move "instruction pointer" to the next instruction IF NOT already moved by "jump" or "branch" instruction
    if not instruction_pointer_updated:
        # It increases by 4 bytes because every RISC-V instruction is 32-bit in size. 32 bits == 4 bytes
        registers.instruction_pointer += 4


    # In RISC-V, register x0 is hardwired to zero, and cannot be changed
    # To implement this we use following hack to reset register x0 to zero after every instruction execution
    # Otherwise we would need to create functions for reading/writing to integer registers just like
    # we do for CSR registers
    registers.integer_regs[0] = 0
    pass


def emulate_cpu():

    registers = Registers()

    # The emulator will have 64MB of RAM, with the content of the Linux image placed at the beginning of RAM
    memory = Memory(linux_image_path='Linux_image_6_1_14_RV32IMA_NoMMU', RAM_size=64*1024*1024)

    while True:
        execute_single_CPU_instruction(registers, memory)


# Main starting point of this program/script
if __name__ == '__main__':
    emulate_cpu()
