#! /usr/bin/env python3

# Implementing RISC-V CPU emulator - only RV32IM instruction set (32-bit integer + multiplication/division)

from instruction_executer import execute_instruction
from memory import Memory, linux_instructions
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

    # Fetch the instruction number/value from the memory
    instruction = memory.get_4_bytes__little_endian(registers.instruction_pointer)

    print(f"Instruction value:   0x{instruction:08x} \n")

    # Execute the instruction
    instruction_pointer_updated = execute_instruction(registers, memory, instruction)

    # Move "instruction pointer" to the next instruction IF NOT already moved by "jump" or "branch" instruction
    if not instruction_pointer_updated:
        # It increases by 4 bytes because every RISC-V instruction is 32-bit in size. 32 bits == 4 bytes
        registers.instruction_pointer += 4
    pass


def emulate_cpu():

    registers = Registers()
    memory = Memory(linux_instructions)

    while True:
        execute_single_CPU_instruction(registers, memory)


# Main starting point of this program/script
if __name__ == '__main__':
    emulate_cpu()
