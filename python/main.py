#! /usr/bin/env python3

# Implementing RV32IM (Integer + multiplication/division)

# TODO
#   - Make a list of instructions to implement
#       - Make a list of "base" instructions
#       - Make a list of I instructions
#       - Make a list of M instructions

# DOCU:
#   - https://itnext.io/risc-v-instruction-set-cheatsheet-70961b4bbe8
#   - https://en.wikipedia.org/wiki/RISC-V#Design
#   - https://fraserinnovations.com/risc-v/risc-v-instruction-set-explanation/
#   - https://riscv.org/wp-content/uploads/2017/05/riscv-spec-v2.2.pdf

# QUICK REFERENCE
#
# Instuction list     - https://upload.wikimedia.org/wikipedia/commons/f/fe/RV32IMAC_Instruction_Set.svg
# Instruction format  - https://miro.medium.com/v2/resize:fit:4800/format:webp/1*Mznpgo4kFWIayagpftLmTg.png
# Instruction opcodes - https://www.cs.sfu.ca/~ashriram/Courses/CS295/assets/notebooks/RISCV/RISCV_CARD.pdf
# Instruction decoder - https://luplab.gitlab.io/rvcodecjs
# ISA Manual          - https://five-embeddev.com/riscv-isa-manual/latest/csr.html


# The first 128 bytes of the Linux kernel code
linux_code = [
    111,   0, 192,   5,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
     80,  87,  55,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
      2,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
     82,  73,  83,  67,  86,   0,   0,   0,  82,  83,  67,   5,   0,   0,   0,   0,
     23,  37,   0,   0,  19,   5, 197, 199, 115,  16,  85,  48, 115,  16,   0,  52,
    103, 128,   0,   0, 115,   0,  80,  16, 111, 240, 223, 255, 115,  16,  64,  48,
    115,  16,  64,  52,  15,  16,   0,   0, 239,   0, 128,  10,  23,   5,   0,   0,
     19,   5, 197,   1, 115,  16,  85,  48,  19,   5, 240, 255, 115,  16,   5,  59
]

PC = 0x80000000
registers = [0] * 32


def read_memory(address):
    if address >= 0x80000000:
        image_addr = address - 0x80000000
        return linux_code[image_addr]

    return 0


def get_instruction_subtype__funct3(instruction):
    val = instruction & 0b111000000000000
    val = val >> 12
    return val


def get_instruction_destination__register_rd(instruction):
    val = instruction & 0b000111110000000
    val = val >> 7
    return val


def get_instruction_source_register__rs1(instruction):
    val = instruction & 0b11111000000000000000
    return val >> 15


def get_instruction_hardcoded_number__immediate_i(instruction):
    val = instruction & 0b11111111111000000000000000000000
    val = val >> 20
    return val


def get_instruction_hardcoded_number__immediate_j(value):
    # Extract bits by applying a mask and shifting
    # TODO: I will try to make this more readable.
    #       The encoding of immediate value for (jump) J type of instruction is very messy
    #       and I actually had to draw a picture/diagram of it to see what is going on here
    bit_31 = (value & (1 << 31)) >> 31
    bits_19_to_12 = (value & (((1 << 8) - 1) << 12)) >> 12
    bit_20 = (value & (1 << 20)) >> 20
    bits_30_to_25 = (value & (((1 << 6) - 1) << 25)) >> 25
    bits_24_to_21 = (value & (((1 << 4) - 1) << 21)) >> 21

    val = (bit_31 << 20) | (bits_19_to_12 << 12) | (bit_20 << 11) | (bits_30_to_25 << 5) | (bits_24_to_21 << 1)
    return val


def read_32_bits_from_memory__little_endian(address):
    byte0 = read_memory(address)
    byte1 = read_memory(address + 1)
    byte2 = read_memory(address + 2)
    byte3 = read_memory(address + 3)

    value = (byte3 << 24) + (byte2 << 16) + (byte1 << 8) + byte0

    return value


def execute_single_CPU_instruction():
    global PC

    print(f"PC: {hex(PC)}")

    instruction = read_32_bits_from_memory__little_endian(PC)

    opcode = instruction & 0b01111111

    #print(f"Opcode: {hex(opcode)}")

    #print_I_type_instruction(instruction)

    if opcode == 0x6f: # jal
        print_J_type_instruction(instruction)

        rd = get_instruction_destination__register_rd(instruction)

        immediate_val = get_instruction_hardcoded_number__immediate_j(instruction)
        if rd > 0:
            registers[rd] = PC + 4

        PC = PC + immediate_val
        pass
    else:
        print(f"[ERROR] Instruction not implemented: {hex(instruction)}")
        return
    pass


def print_I_type_instruction(instruction):
    opcode = instruction & 0b000000001111111
    rd = get_instruction_destination__register_rd(instruction)
    funct3 = get_instruction_subtype__funct3(instruction)
    rs1 = get_instruction_source_register__rs1(instruction)
    imm = get_instruction_hardcoded_number__immediate_i(instruction)

    print(f"Parsing I-type values from: {hex(instruction)}")
    print(f"  Opcode: {hex(opcode)}")
    print(f"  rd:     {hex(rd)}")
    print(f"  funct3: {hex(funct3)} \n")
    print(f"  rs1:     {hex(rs1)} \n")
    print(f"  imm:    {hex(imm)} \n")
    pass

def print_J_type_instruction(instruction):
    opcode = instruction & 0b000000001111111
    rd = get_instruction_destination__register_rd(instruction)
    imm = get_instruction_hardcoded_number__immediate_j(instruction)

    print(f"Parsing I-type values from: {hex(instruction)}")
    print(f"  Opcode: {hex(opcode)}")
    print(f"  rd:     {hex(rd)}")
    print(f"  imm:    {hex(imm)} \n")
    pass


if __name__ == '__main__':

    for i, value_32 in enumerate(linux_code[:25]):
        print(f"{hex(i*4)}: {hex(value_32)}")

    print("\n\n")

    for x in range(3):
        execute_single_CPU_instruction()
    pass

