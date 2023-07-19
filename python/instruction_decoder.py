
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
