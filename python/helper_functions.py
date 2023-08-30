

def interpret_as_32_bit_signed_value(signed_value):
    ret_val = signed_value

    if signed_value & 0x80000000 != 0:
        ret_val = -((~signed_value & 0xFFFFFFFF) + 1)

    return ret_val


def interpret_as_20_bit_signed_value(signed_value):
    ret_val = signed_value

    if signed_value & 0x00080000 != 0:
        ret_val = -((~signed_value & 0x000FFFFF) + 1)

    return ret_val


def interpret_as_21_bit_signed_value(signed_value):
    ret_val = signed_value

    if signed_value & 0x00100000 != 0:
        ret_val = -((~signed_value & 0x000FFFFF) + 1)

    return ret_val


def interpret_as_12_bit_signed_value(signed_value):
    ret_val = signed_value

    if signed_value & 0x00000800 != 0:
        ret_val = -((~signed_value & 0x00000FFF) + 1)

    return ret_val

