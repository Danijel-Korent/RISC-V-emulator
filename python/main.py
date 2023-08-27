#! /usr/bin/env python3
from emulator_logger import Emulator_logger
# Implementing RISC-V CPU emulator - only RV32IMA instruction set (32-bit integer + multiplication/division + atomics)

from instruction_executer import execute_instruction
from memory import Memory
from registers import Registers


LINUX_IMAGE_PATH = 'Linux_kernel_image/Linux_image_6_1_14_RV32IMA_NoMMU'
RAM_SIZE = 100*1024*1024


def execute_single_CPU_instruction(registers, memory, logger):

    # Fetch
    instruction = memory.get_4_bytes__little_endian(registers.instruction_pointer)

    logger.register_one_CPU_step(registers, instruction)

    # Execute
    instruction_pointer_updated = execute_instruction(registers, memory, instruction, logger)

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

    logger = Emulator_logger(start_traceout_at_instruction_no=112049)

    registers = Registers()

    # The emulator will have 64MB of RAM, with the content of the Linux image placed at the beginning of RAM
    memory = Memory(LINUX_IMAGE_PATH, RAM_SIZE)

    while True:
        execute_single_CPU_instruction(registers, memory, logger)


# Main starting point of this program/script
if __name__ == '__main__':
    emulate_cpu()
