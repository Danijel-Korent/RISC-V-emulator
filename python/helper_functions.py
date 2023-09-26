import ctypes


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


# This whole function can be replaced with just (value & 0xFFFFFFFF)
def convert_to_32_bit_unsigned_value(value):
    return ctypes.c_uint32(value).value


# SIGN-EXTEND THE VALUE
# If the last (12th) bit of the immediate is set to '1', it means that the value is negative (if we
# interpreted it as signed value)
# When loading this 12-bit long value into a 32-bit long register, we want to keep that value as negative
# number (and as the exactly same negative value) we need to extend '1's to all additional bits
# For example:
#   1111 is -1 as a 4-bit value. But as a 8-bit value 00001111 it is 15 when we interpret it as signed value
#   If we want to keep -1 when expanding 4-bit value into 8-bit space, we need to add '1's -> 11111111
def sign_extend_12_bit_value(value):
    if value & 0x800 != 0:
        value = value | 0xFFFFF000

    return value
