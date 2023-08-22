#! /usr/bin/env python3

# Implementing RISC-V CPU emulator - only RV32IM instruction set (32-bit integer + multiplication/division)

from instruction_decoder import Instruction_parser

# The first 128 bytes of the compiled Linux kernel code. Linux kernel code compiles into instructions and data,
# so the array contains instructions with some data here and there
linux_instructions = [
    0x6f, 0x00, 0xc0, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x50, 0x57, 0x37, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x52, 0x49, 0x53, 0x43, 0x56, 0x00, 0x00, 0x00, 0x52, 0x53, 0x43, 0x05, 0x00, 0x00, 0x00, 0x00,
    0x17, 0x25, 0x00, 0x00, 0x13, 0x05, 0xc5, 0xc7, 0x73, 0x10, 0x55, 0x30, 0x73, 0x10, 0x00, 0x34,
    0x67, 0x80, 0x00, 0x00, 0x73, 0x00, 0x50, 0x10, 0x6f, 0xf0, 0xdf, 0xff, 0x73, 0x10, 0x40, 0x30,
    0x73, 0x10, 0x40, 0x34, 0x0f, 0x10, 0x00, 0x00, 0xef, 0x00, 0x80, 0x0a, 0x17, 0x05, 0x00, 0x00,
    0x13, 0x05, 0xc5, 0x01, 0x73, 0x10, 0x55, 0x30, 0x13, 0x05, 0xf0, 0xff, 0x73, 0x10, 0x05, 0x3b,
    0x13, 0x05, 0xf0, 0x01, 0x73, 0x10, 0x05, 0x3a, 0x73, 0x25, 0x40, 0xf1, 0x97, 0x11, 0x35, 0x00,
    0x93, 0x81, 0xc1, 0xfe, 0xb7, 0x62, 0x00, 0x00, 0x73, 0xb0, 0x02, 0x30, 0x97, 0x16, 0x35, 0x00,
    0x93, 0x86, 0x46, 0xf6, 0x17, 0x57, 0x37, 0x00, 0x13, 0x07, 0xc7, 0x6a, 0x63, 0xd8, 0xe6, 0x00,
    0x23, 0xa0, 0x06, 0x00, 0x93, 0x86, 0x46, 0x00, 0xe3, 0xcc, 0xe6, 0xfe, 0x13, 0x04, 0x05, 0x00,
    0x93, 0x84, 0x05, 0x00, 0x17, 0x16, 0x35, 0x00, 0x13, 0x06, 0x86, 0xfa, 0x23, 0x20, 0xa6, 0x00,
    0x17, 0xf2, 0x30, 0x00, 0x13, 0x02, 0x02, 0x27, 0x17, 0xe1, 0x30, 0x00, 0x13, 0x01, 0x81, 0xf2,
    0x13, 0x85, 0x04, 0x00, 0x97, 0x90, 0x17, 0x00, 0xe7, 0x80, 0xc0, 0xd3, 0xef, 0xf0, 0x5f, 0xf5,
    0x17, 0xf2, 0x30, 0x00, 0x13, 0x02, 0x02, 0x25, 0x17, 0xe1, 0x30, 0x00, 0x13, 0x01, 0x81, 0xf0,
    0x97, 0x80, 0x17, 0x00, 0xe7, 0x80, 0xc0, 0xee, 0x17, 0x53, 0x17, 0x00, 0x67, 0x00, 0xc3, 0x59,
    0x13, 0x01, 0x00, 0x00, 0x93, 0x01, 0x00, 0x00, 0x13, 0x02, 0x00, 0x00, 0x93, 0x02, 0x00, 0x00,
    0x13, 0x03, 0x00, 0x00, 0x93, 0x03, 0x00, 0x00, 0x13, 0x04, 0x00, 0x00, 0x93, 0x04, 0x00, 0x00,
    0x13, 0x06, 0x00, 0x00, 0x93, 0x06, 0x00, 0x00, 0x13, 0x07, 0x00, 0x00, 0x93, 0x07, 0x00, 0x00,
    0x13, 0x08, 0x00, 0x00, 0x93, 0x08, 0x00, 0x00, 0x13, 0x09, 0x00, 0x00, 0x93, 0x09, 0x00, 0x00,
    0x13, 0x0a, 0x00, 0x00, 0x93, 0x0a, 0x00, 0x00, 0x13, 0x0b, 0x00, 0x00, 0x93, 0x0b, 0x00, 0x00,
    0x13, 0x0c, 0x00, 0x00, 0x93, 0x0c, 0x00, 0x00, 0x13, 0x0d, 0x00, 0x00, 0x93, 0x0d, 0x00, 0x00,
    0x13, 0x0e, 0x00, 0x00, 0x93, 0x0e, 0x00, 0x00, 0x13, 0x0f, 0x00, 0x00, 0x93, 0x0f, 0x00, 0x00,
    0x73, 0x50, 0x00, 0x34, 0x67, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
]


class CPU_state:
    def __init__(self):
        # All CPUs have one register that holds the address of the next instruction to execute
        # Here we also set the initial instruction address. Normal system would have ROM/flash memory (with initial
        # hardcoded bootloader) mapped into this address. We mapped at this address (a small chunk of) Linux kernel
        self.instruction_pointer_register = 0x80000000

        # An array of registers
        # RISC-V has 32 integer registers
        # https://en.wikipedia.org/wiki/RISC-V#Register_sets
        self.integer_registers = [
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                 ]

    def print_register_values(self):
        # just to shorten the variable name
        reg = self.integer_registers

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
        elif register_num == 0x344:
            print(f"Tried to read CSR[0x{register_num:x}]  (register 'mip': Machine Interrupt Pending) \n")
        else:
            print(f"[ERROR] Tried to read unknown CSR register -> CSR[0x{register_num:x}] \n")
            exit()
        return 0

    def write_to_CSR_register(self, register_num, value):
        if register_num == 0x304:
            print(f"Tried to write CSR[0x{register_num:x}] = 0x{value:x}  (register 'mie': Machine Interrupt Enable) \n")
        elif register_num == 0x344:
            print(f"Tried to write CSR[0x{register_num:x}] = 0x{value:x}  (register 'mip': Machine Interrupt Pending) \n")
        else:
            print(f"[ERROR] Tried to write unknown CSR register -> CSR[0x{register_num:x}] = 0x{value:x} \n")
            exit()
        pass

class Memory:
    def __init__(self, linux_image):
        self.linux_instructions = linux_image

    # Returns a value stored at specified address
    # WARNING:
    #   Currently RAM is not implemented at all. Only the Linux kernel code at 0x80000000 is accessible. Everything else
    #   just returns zero.
    def get_1_byte(self, address):
        if address >= 0x80000000:
            image_addr = address - 0x80000000
            return self.linux_instructions[image_addr]

        return 0

    # Read 32bits/4bytes starting from specified address
    # RISC-V starts in little endian mode, therefor we need to read data as little endian order
    def get_4_bytes__little_endian(self, address):
        # When you read byte-by-byte you will get the same value in both little endian CPU (LE) and big endian CPU (BE)
        # But if you read more than a byte into a register, LE and BE CPUs will put individual bytes into different
        # places in the register. It is similar to how some cultures read from left-to-right and some from right-to-left
        # If we imagine that single byte contains only single digit then following 4-bytes in memory [1,2,3,4] are read
        # by one CPU as number "1234" while a CPU with opposite endianness will read the same 4 bytes as a number "4321"
        #
        # Same is for writing a register into memory. In case of 32-bit (4 byte) register, LE and BE CPUs will
        # put individual bytes of register into different places in memory.
        # https://en.wikipedia.org/wiki/Endianness#Overview
        byte0 = self.get_1_byte(address)
        byte1 = self.get_1_byte(address + 1)
        byte2 = self.get_1_byte(address + 2)
        byte3 = self.get_1_byte(address + 3)

        value = (byte3 << 24) + (byte2 << 16) + (byte1 << 8) + byte0

        return value


instruction_no_counter = 0


def execute_single_CPU_instruction(cpu_state, memory):
    global instruction_no_counter

    instruction_no_counter += 1

    cpu_state.print_register_values()

    print("\n===============================")
    print(f"Instruction no.:     {instruction_no_counter}")
    print("===============================")
    print(f"Instruction pointer: 0x{cpu_state.instruction_pointer_register:08x}")

    # Read the instruction value from the memory
    instruction = memory.get_4_bytes__little_endian(cpu_state.instruction_pointer_register)

    print(f"Instruction value:   0x{instruction:08x} \n")

    # Extract the 'operation/instruction' type
    opcode = instruction & 0b01111111

    instruction_pointer_updated = False

    if opcode == 0x0f:  # Instruction 'fence'
        # Fence is only relevant for more complex CPU implementations
        print(f"Executed instruction -> fence \n")
        pass
    elif opcode == 0x13:  # Arithmetic/logic instructions with immediate value hardcoded into instruction
        Instruction_parser.print_I_type_instruction(instruction)

        immediate_val = Instruction_parser.get_hardcoded_number__immediate_i(instruction)

        source_reg = Instruction_parser.get_source_register__rs(instruction)
        destination_reg = Instruction_parser.get_destination_register__rd(instruction)

        instruction_subtype = Instruction_parser.get_subtype__funct3(instruction)

        if instruction_subtype == 0x0:  # Instructions 'addi'
            cpu_state.integer_registers[destination_reg] = cpu_state.integer_registers[source_reg] + immediate_val

            print(f"Executed instruction -> addi x{destination_reg}, x{source_reg}, {immediate_val}  (Add immediate)\n")
            pass
        else:
            print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
            quit()
        pass
    elif opcode == 0x6f:  # instruction "jal"
        instruction_pointer_updated = True
        Instruction_parser.print_J_type_instruction(instruction)

        rd = Instruction_parser.get_destination_register__rd(instruction)

        immediate_val = Instruction_parser.get_hardcoded_number__immediate_j(instruction)
        cpu_state.integer_registers[rd] = cpu_state.instruction_pointer_register + 4

        # Update instruction pointer to a new value
        cpu_state.instruction_pointer_register = cpu_state.instruction_pointer_register + immediate_val

        print(f"Executed instruction -> jal {rd}, {immediate_val}  (Jump and Link)\n")
        pass
    elif opcode == 0x73:  # CSR instructions
        Instruction_parser.print_I_type_instruction(instruction)

        instruction_subtype = Instruction_parser.get_subtype__funct3(instruction)

        # In immediate field of the instruction an CSR address value is encoded
        CSR_address = Instruction_parser.get_hardcoded_number__immediate_i(instruction)

        source_reg      = Instruction_parser.get_source_register__rs(instruction)
        destination_reg = Instruction_parser.get_destination_register__rd(instruction)

        if instruction_subtype == 0x001:  # instruction "csrrw"
            current_CSR_reg_value = cpu_state.read_from_CSR_register(CSR_address)
            cpu_state.write_to_CSR_register(CSR_address, cpu_state.integer_registers[source_reg])
            cpu_state.integer_registers[destination_reg] = current_CSR_reg_value

            print(f"Executed instruction -> csrrw {destination_reg}, {CSR_address}, {source_reg}  (Control and Status Register Read-Write)\n")
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
        cpu_state.instruction_pointer_register += 4
    pass


def emulate_cpu():

    cpu_state = CPU_state()
    memory = Memory(linux_instructions)

    while True:
        execute_single_CPU_instruction(cpu_state, memory)


# Main starting point of this program/script
if __name__ == '__main__':
    emulate_cpu()
