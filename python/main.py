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


import struct


def load_32bit_values(filename):
    with open(filename, 'rb') as f:
        data = f.read()

    return [struct.unpack('<i', data[i:i+4])[0] for i in range(0, len(data), 4)]


image = load_32bit_values('test_image')

PC = 0x80000000
registers = [0] * 32


def read_memory(address):
    if address >= 0x80000000:
        addr = address - 0x80000000
        image_addr = addr >> 2 # addr / 4
        return image[image_addr]

    return 0


def get_instruction_funct3(instruction):
    val = instruction & 0b111000000000000
    val = val >> 12
    return val


def get_instruction_rd(instruction):
    val = instruction & 0b000111110000000
    val = val >> 7
    return val


def get_instruction_rs1(instruction):
    val = instruction & 0b11111000000000000000
    return val >> 15



def get_instruction_immediate_i(instruction):
    val = instruction & 0b11111111111000000000000000000000
    val = val >> 20
    return val

def get_instruction_immediate_j(value):
    # Extract bits by applying a mask and shifting
    bit_31 = (value & (1 << 31)) >> 31
    bits_19_to_12 = (value & (((1 << 8) - 1) << 12)) >> 12
    bit_20 = (value & (1 << 20)) >> 20
    bits_30_to_25 = (value & (((1 << 6) - 1) << 25)) >> 25
    bits_24_to_21 = (value & (((1 << 4) - 1) << 21)) >> 21

    val = (bit_31 << 20) | (bits_19_to_12 << 12) | (bit_20 << 11) | (bits_30_to_25 << 5) | (bits_24_to_21 << 1)
    #val = val << 1

    # Rearrange the bits in the order [31|19:12|20|30:25|24:21] and set last bit to 0
    return val


def CPU_execute_single_step():
    global PC

    print(f"PC: {hex(PC)}")

    instruction = read_memory(PC)

    opcode = instruction & 0b01111111

    #print(f"Opcode: {hex(opcode)}")

    #print_I_type_instruction(instruction)

    if opcode == 0x6f: # jal
        print_J_type_instruction(instruction)

        rd = get_instruction_rd(instruction)

        immediate_val = get_instruction_immediate_j(instruction)
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
    rd = get_instruction_rd(instruction)
    funct3 = get_instruction_funct3(instruction)
    rs1 = get_instruction_rs1(instruction)
    imm = get_instruction_immediate_i(instruction)

    print(f"Parsing I-type values from: {hex(instruction)}")
    print(f"  Opcode: {hex(opcode)}")
    print(f"  rd:     {hex(rd)}")
    print(f"  funct3: {hex(funct3)} \n")
    print(f"  rs1:     {hex(rs1)} \n")
    print(f"  imm:    {hex(imm)} \n")
    pass

def print_J_type_instruction(instruction):
    opcode = instruction & 0b000000001111111
    rd = get_instruction_rd(instruction)
    imm = get_instruction_immediate_j(instruction)

    print(f"Parsing I-type values from: {hex(instruction)}")
    print(f"  Opcode: {hex(opcode)}")
    print(f"  rd:     {hex(rd)}")
    print(f"  imm:    {hex(imm)} \n")
    pass


if __name__ == '__main__':

    for i, value_32 in enumerate(image[:25]):
        print(f"{hex(i*4)}: {hex(value_32)}")

    print("\n\n")

    for x in range(3):
        CPU_execute_single_step()
    pass

