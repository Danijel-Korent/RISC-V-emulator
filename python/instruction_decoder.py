
def get_instruction_destination__register_rd(instruction):
    val = instruction & 0b000111110000000
    val = val >> 7
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


def print_J_type_instruction(instruction):
    opcode = instruction & 0b000000001111111
    rd = get_instruction_destination__register_rd(instruction)
    imm = get_instruction_hardcoded_number__immediate_j(instruction)

    print(f"Parsing I-type values from instruction: 0x{instruction:08x}")
    print(f"  Opcode: {hex(opcode)}")
    print(f"  rd:     {hex(rd)}")
    print(f"  imm:    {hex(imm)} \n")
    pass


if __name__ == '__main__':
    print(f"\nExecuting:\n\t{__file__} \n")
    print("Hopefully here we will have tests for functions in this file")
