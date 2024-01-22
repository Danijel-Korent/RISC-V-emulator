#! /usr/bin/env python3
from address_space import Address_Space
from device_timer_CLINT import Device_Timer_CLINT
from device_uart_8250 import Device_UART_8250
from emulator_logger import Emulator_logger
# Implementing RISC-V CPU emulator - only RV32IMA instruction set (32-bit integer + multiplication/division + atomics)

from cpu.instruction_executer import execute_instruction
from RAM_memory import RAM_memory
from cpu.registers import Registers, CSR_Registers
from config import *
from cpu.trap_and_interrupt_handler import Trap_And_Interrupt_Handler


# TODO: rename to execute_next_CPU_instruction
def execute_single_CPU_instruction(registers, CSR_registers, trap_and_interrupt_handler, memory, logger):

    # Fetch
    instruction = memory.get_4_bytes__little_endian(registers.instruction_pointer)

    # TODO: Move this into the execute_instruction()
    logger.register_one_CPU_step(registers, instruction, memory)

    # Execute
    # TODO: To many arguments. Group somo of them into "CPU_state" or maybe just "CPU"
    instruction_pointer_updated = execute_instruction(instruction, registers, CSR_registers, trap_and_interrupt_handler, memory, logger)

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

    logger = Emulator_logger(START_TRACEOUT_AT_INSTRUCTION_NO, LOGGER_REPORT_TYPE)

    ram_memory = RAM_memory(LINUX_IMAGE_PATH, DEVICE_TREE_PATH, RAM_SIZE)

    registers = Registers(logger)
    registers.integer_regs[11] = START_ADDRESS_OF_RAM + ram_memory.get_device_tree_RAM_address()
    # print(f"Location of DTB: {registers.integer_regs[11]:08x}") # TODO: Make this less confusing

    trap_and_interrupt_handler = Trap_And_Interrupt_Handler(registers, logger)
    CSR_registers = CSR_Registers(trap_and_interrupt_handler, logger)

    # TODO: It would probably be smart to make logger a singleton
    device_UART_8250 = Device_UART_8250(logger)
    device_timer_CLINT = Device_Timer_CLINT(logger, registers, trap_and_interrupt_handler) # TODO: Only pass a function for triggering the interrupt

    # If need for more devices appears, it would probably be smarter to pass a list of objects with a common interface
    address_space = Address_Space(ram_memory, device_UART_8250, device_timer_CLINT)

    while True:
        device_timer_CLINT.update()
        execute_single_CPU_instruction(registers, CSR_registers, trap_and_interrupt_handler, address_space, logger)
        trap_and_interrupt_handler.update()


# Main starting point of this program/script
if __name__ == '__main__':
    emulate_cpu()
