#! /usr/bin/env python3

# Implementing RISC-V CPU emulator - only RV32IM instruction set (32-bit integer + multiplication/division)

from instruction_decoder import Instruction_parser

# The first 128 bytes of the compiled Linux kernel code. Linux kernel code compiles into instructions and data,
# so the array contains instructions with some data here and there
linux_instructions = [
    111,   0, 192,   5,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
     80,  87,  55,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
      2,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
     82,  73,  83,  67,  86,   0,   0,   0,  82,  83,  67,   5,   0,   0,   0,   0,
     23,  37,   0,   0,  19,   5, 197, 199, 115,  16,  85,  48, 115,  16,   0,  52,
    103, 128,   0,   0, 115,   0,  80,  16, 111, 240, 223, 255, 115,  16,  64,  48,
    115,  16,  64,  52,  15,  16,   0,   0, 239,   0, 128,  10,  23,   5,   0,   0,
     19,   5, 197,   1, 115,  16,  85,  48,  19,   5, 240, 255, 115,  16,   5,  59
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

    def read_from_CSR_register(self, register_num):
        if register_num == 0x304:
            print(f"Tried to read CSR[0x{register_num:x}]  (register 'mie') \n")
        else:
            exit()
        return 0

    def write_to_CSR_register(self, register_num, value):
        if register_num == 0x304:
            print(f"Tried to write CSR[0x{register_num:x}] = {value}  (register 'mie') \n")
        else:
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
    print(f"Instruction no.:     {instruction_no_counter}")
    print(f"Instruction pointer: 0x{cpu_state.instruction_pointer_register:08x}")

    # Read the instruction from the memory
    instruction = memory.get_4_bytes__little_endian(cpu_state.instruction_pointer_register)

    print(f"Instruction value:   0x{instruction:08x} \n")

    # Extract the 'operation/instruction' type
    opcode = instruction & 0b01111111

    if opcode == 0x6f:  # instruction "jal"
        Instruction_parser.print_J_type_instruction(instruction)

        rd = Instruction_parser.get_destination_register__rd(instruction)

        immediate_val = Instruction_parser.get_hardcoded_number__immediate_j(instruction)
        cpu_state.integer_registers[rd] = cpu_state.instruction_pointer_register + 4

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
    pass


def emulate_cpu():

    cpu_state = CPU_state()
    memory = Memory(linux_instructions)

    while True:
        execute_single_CPU_instruction(cpu_state, memory)


# Main starting point of this program/script
if __name__ == '__main__':
    emulate_cpu()
