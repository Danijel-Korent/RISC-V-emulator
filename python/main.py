#! /usr/bin/env python3

# Implementing RISC-V CPU emulator - only RV32IM instruction set (32-bit integer + multiplication/division)

from instruction_decoder import Instruction_parser
from memory import Memory, linux_instructions


class Registers:
    def __init__(self):
        # All CPUs have one register that holds the address of the next instruction to execute
        # Here we also set the initial instruction address. Normal system would have ROM/flash memory (with initial
        # hardcoded bootloader) mapped into this address. We mapped at this address (a small chunk of) Linux kernel
        self.instruction_pointer = 0x80000000

        # An array of registers
        # RISC-V has 32 integer registers
        # https://en.wikipedia.org/wiki/RISC-V#Register_sets
        self.integer_regs = [
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                 ]

        self.CSR_mscratch = 0

    def print_register_values(self):
        # just to shorten the variable name
        reg = self.integer_regs

        for i in range(8):
            offset = i*4
            for x in range(4):
                reg_no = offset + x
                print(f"x{reg_no:02}: {reg[reg_no]:08x}, ", end='')
            # just for new line
            print("")

    def read_from_CSR_register(self, register_num):
        if register_num == 0x304:
            print(f"Tried to read CSR[0x{register_num:x}]  (register 'mie': Machine Interrupt Enable) \n")
        elif register_num == 0x340:
            print(f"Tried to read CSR[0x{register_num:x}]  (register 'mscratch': Scratch register) \n")
            return self.CSR_mscratch
        elif register_num == 0x344:
            print(f"Tried to read CSR[0x{register_num:x}]  (register 'mip': Machine Interrupt Pending) \n")
        else:
            print(f"[ERROR] Tried to read unknown CSR register -> CSR[0x{register_num:x}] \n")
            exit()
        return 0

    def write_to_CSR_register(self, register_num, value):
        if register_num == 0x304:
            print(f"Tried to write CSR[0x{register_num:x}] = 0x{value:x}  (register 'mie': Machine Interrupt Enable) \n")
        elif register_num == 0x340:
            print(f"Tried to write CSR[0x{register_num:x}] = 0x{value:x}  (register 'mscratch': Scratch register) \n")
            self.CSR_mscratch = value
        elif register_num == 0x344:
            print(f"Tried to write CSR[0x{register_num:x}] = 0x{value:x}  (register 'mip': Machine Interrupt Pending) \n")
        else:
            print(f"[ERROR] Tried to write unknown CSR register -> CSR[0x{register_num:x}] = 0x{value:x} \n")
            exit()
        pass


instruction_no_counter = 0


def execute_single_CPU_instruction(registers, memory):
    global instruction_no_counter

    instruction_no_counter += 1

    registers.print_register_values()

    print("\n===============================")
    print(f"Instruction no.:     {instruction_no_counter}")
    print("===============================")
    print(f"Instruction pointer: 0x{registers.instruction_pointer:08x}")

    # Read the instruction value from the memory
    instruction = memory.get_4_bytes__little_endian(registers.instruction_pointer)

    print(f"Instruction value:   0x{instruction:08x} \n")

    # Extract the 'operation/instruction' type
    opcode = instruction & 0b01111111

    instruction_pointer_updated = False

    # --- Instruction 'FENCE' ---
    if opcode == 0x0f:
        # Fence is only relevant for more complex CPU implementations
        print(f"Ignored instruction -> fence \n")
        pass

    # --- Arithmetic/Logic instructions with immediate ---
    elif opcode == 0x13:
        # Arithmetic/logic instructions with immediate value hardcoded into instruction
        Instruction_parser.print_I_type_instruction(instruction)

        instruction_subtype, destination_reg, source_reg, immediate_val = Instruction_parser.decode_I_type(instruction)

        # --- Instruction 'ADDI' ---
        if instruction_subtype == 0x0:
            registers.integer_regs[destination_reg] = registers.integer_regs[source_reg] + immediate_val

            print(f"Executed instruction -> addi x{destination_reg}, x{source_reg}, {immediate_val}  (Add immediate)\n")
            pass
        else:
            print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
            quit()
        pass

    # --- instruction "JAL" ---
    elif opcode == 0x6f:
        instruction_pointer_updated = True
        Instruction_parser.print_J_type_instruction(instruction)

        destination_reg, immediate_val = Instruction_parser.decode_J_type(instruction)

        registers.integer_regs[destination_reg] = registers.instruction_pointer + 4

        # Update instruction pointer to a new value
        registers.instruction_pointer = registers.instruction_pointer + immediate_val

        print(f"Executed instruction -> jal {destination_reg}, {immediate_val}  (Jump and Link)\n")
        pass

    # --- CSR instructions ---
    elif opcode == 0x73:
        Instruction_parser.print_I_type_instruction(instruction)

        instruction_subtype, destination_reg, source_reg, immediate_val = Instruction_parser.decode_I_type(instruction)

        # In immediate field of the instruction an CSR address value is encoded
        CSR_address = immediate_val

        # --- Instruction "CSRRW" ---
        if instruction_subtype == 0x1:
            registers.integer_regs[destination_reg] = registers.read_from_CSR_register(CSR_address)
            registers.write_to_CSR_register(CSR_address, registers.integer_regs[source_reg])

            print(f"Executed instruction -> csrrw {destination_reg}, {CSR_address}, {source_reg}  (Control and Status Register Read-Write)\n")
            pass

        # --- Instruction "CSRRWI" ---
        elif instruction_subtype == 0x5:
            # Immediate values is in this case encoded into bit field that
            # usually holds source register number (RS bit field)
            immediate_val = source_reg

            registers.integer_regs[destination_reg] = registers.read_from_CSR_register(CSR_address)
            registers.write_to_CSR_register(CSR_address, immediate_val)

            print(f"Executed instruction -> csrrwi {destination_reg}, {CSR_address}, {immediate_val}  (Control and Status Register Read-Write Immediate)\n")
            pass
        else:
            print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
            quit()
        pass
    else:
        print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
        quit()

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
