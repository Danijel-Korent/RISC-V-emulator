from helper_functions import interpret_as_32_bit_signed_value, interpret_as_12_bit_signed_value, \
    interpret_as_20_bit_signed_value, interpret_as_21_bit_signed_value, convert_to_32_bit_unsigned_value, \
    sign_extend_12_bit_value
from instruction_decoder import Instruction_parser


def execute_instruction(registers, memory, instruction, logger):

    # Extract the 'operation/instruction' type
    opcode = instruction & 0b01111111

    instruction_pointer_updated = False

    # --- 'Load' instructions ---
    if opcode == 0x03:
        instruction_subtype, destination_reg, source_reg, immediate_val = Instruction_parser.decode_I_type(instruction)

        # Immediate is a signed value for all 'load' instructions
        immediate_val = interpret_as_12_bit_signed_value(immediate_val)

        base_address = registers.integer_regs[source_reg]
        offset = immediate_val

        address = base_address + offset

        # --- Instruction 'LB' ---
        if instruction_subtype == 0:
            value = memory.get_1_byte(address)

            # SIGN-EXTEND THE BYTE
            # If the last (8th) bit of the byte is set to '1', it means that the value is negative (if we interpreted it
            # as signed value)
            # When loading this 8-bit long byte into a 32-bit long register, ff we want to keep that value as negative
            # number (and as the same negative value) we need to extend '1's to all additional bits
            # For example:
            #   1111 is -1 as a 4-bit value. But as a 8-bit value 00001111 it is 15 when we interpret it as signed value
            #   If we want to keep -1 when expanding 4-bit value into 8-bit space, we need to add '1's -> 11111111
            # TODO: Turn into function
            if value & 0b10000000 != 0:
                value = value | 0xFFFFFF00

            registers.integer_regs[destination_reg] = value

            logger.register_executed_instruction(f"lb x{destination_reg}, {immediate_val}(x{source_reg})  (Load Byte, 8-bit - With sign extension)")
            pass

        # --- Instruction 'LH' ---
        elif instruction_subtype == 1:
            value = memory.get_2_bytes__little_endian(address)

            # TODO: Turn into function
            if value & 0x8000 != 0:
                value = value | 0xFFFF0000

            registers.integer_regs[destination_reg] = value

            if value & 0x8000 != 0:
                #quit()
                pass
            logger.register_executed_instruction(f"lh x{destination_reg}, {immediate_val}(x{source_reg})  (Load Half-word, 16-bit - With sign extension)")
            pass


        # --- Instruction 'LW' ---
        elif instruction_subtype == 2:
            value = memory.get_4_bytes__little_endian(address)

            registers.integer_regs[destination_reg] = value

            logger.register_executed_instruction(f"lw x{destination_reg}, {immediate_val}(x{source_reg})  (Load Word, 32-bit)")
            pass

        # --- Instruction 'LBU' ---
        elif instruction_subtype == 4:
            value = memory.get_1_byte(address)

            registers.integer_regs[destination_reg] = value

            logger.register_executed_instruction(f"lbu x{destination_reg}, {immediate_val}(x{source_reg})  (Load Byte, 8-bit - Unsigned)")
            pass

        # --- Instruction 'LHU' ---
        elif instruction_subtype == 5:
            value = memory.get_2_bytes__little_endian(address)

            registers.integer_regs[destination_reg] = value

            logger.register_executed_instruction(f"lhu x{destination_reg}, {immediate_val}(x{source_reg})  (Load Half-word, 16-bit - Unsigned)")
            pass
        else:
            print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
            quit()
        pass

    # --- Instruction 'FENCE' ---
    elif opcode == 0x0f:
        # Fence is only relevant for more complex CPU implementations
        logger.register_executed_instruction(f"fence (Ignored instruction)")
        pass

    # --- Arithmetic/Logic instructions with immediate ---
    elif opcode == 0x13:
        # Arithmetic/logic instructions with immediate value hardcoded into instruction
        # Instruction_parser.print_I_type_instruction(instruction)

        instruction_subtype, destination_reg, source_reg, immediate_val = Instruction_parser.decode_I_type(instruction)

        source_reg_value = registers.integer_regs[source_reg]

        # --- Instruction 'ADDI' ---
        if instruction_subtype == 0:
            sign = ""

            # The first bit (MSB) tells if the values is negative or not
            # If the first bit of the value is set to 1, then the values is negative, encoded as Two's_complement
            # https://en.wikipedia.org/wiki/Two's_complement
            # TODO: Just replace with helper functions
            if (immediate_val & 0b100000000000) == 0:
                registers.integer_regs[destination_reg] = source_reg_value + immediate_val
            else:
                immediate_val = (~immediate_val & 0xFFF) + 1
                registers.integer_regs[destination_reg] = source_reg_value - immediate_val
                sign = "-"

            # Shorten the register value to 32 bits if it's longer than that after add/sub
            registers.integer_regs[destination_reg] = registers.integer_regs[destination_reg] & 0xFFFFFFFF

            logger.register_executed_instruction(f"addi x{destination_reg}, x{source_reg}, {sign}{immediate_val}  (Add immediate)")
            pass

        # --- Instruction 'SLLI' ---
        elif instruction_subtype == 1:
            # There are only 32 bits in registers so the valid immediate values are up to 2**5
            if immediate_val & 0x111111100000 != 0:
                print(f"[ERROR] SLLI: Invalid instruction encoding !!")
                quit()

            value_to_be_shifted = source_reg_value
            shift_amount = immediate_val & 0b11111  # Get only the lower 5 bits of the immediate

            result = value_to_be_shifted << shift_amount

            registers.integer_regs[destination_reg] = result & 0xFFFFFFFF  # Shorten to 32 bits

            logger.register_executed_instruction(f"slli x{destination_reg}, x{source_reg}, {immediate_val}  (Shift Left Logical - Immediate)")
            pass

        # --- instruction "SLTIU" ---
        elif instruction_subtype == 3:

            if source_reg_value < immediate_val:
                result = 1
            else:
                result = 0

            registers.integer_regs[destination_reg] = result

            logger.register_executed_instruction(f"sltiu x{destination_reg}, x{source_reg}, {immediate_val}  (Set Less Than - Immediate Unsigned)")
            pass

        # --- Instruction 'XORI' ---
        elif instruction_subtype == 4:

            # SIGN-EXTEND THE IMMEDIATE
            # If the last (12th) bit of the immediate is set to '1', it means that the value is negative (if we
            # interpreted it as signed value)
            # When loading this 12-bit long value into a 32-bit long register, we want to keep that value as negative
            # number (and as the exactly same negative value) we need to extend '1's to all additional bits
            # For example:
            #   1111 is -1 as a 4-bit value. But as a 8-bit value 00001111 it is 15 when we interpret it as signed value
            #   If we want to keep -1 when expanding 4-bit value into 8-bit space, we need to add '1's -> 11111111
            immediate_val = sign_extend_12_bit_value(immediate_val)

            result = source_reg_value ^ immediate_val

            registers.integer_regs[destination_reg] = result

            logger.register_executed_instruction(f"xori x{destination_reg}, x{source_reg}, {immediate_val}  (bitwise XOR - Immediate)")
            pass

        # Instructions 'SRLI' and 'SRAI'
        elif instruction_subtype == 5:
            # For 'SRLI' and 'SRAI' the "immediate value filed" actually consists of two encoded fields - type and value

            #                      Shift instruction type     encoded value
            # Immediate bit no. |  12 11 10 09 08 07 06 05 | 04 03 02 01 00
            #                   |  ty ty ty ty ty ty ty ty | im im im im im

            # Shift the immediate to get the shift instruction type
            shift_instruction_type = immediate_val >> 5

            # Store encoded value into separate variable to be less confusing
            shift_amount = immediate_val & 0b00000000011111

            # --- Instruction 'SRLI' ---
            if shift_instruction_type == 0x00:

                result = source_reg_value >> shift_amount

                registers.integer_regs[destination_reg] = result

                logger.register_executed_instruction(f"srli x{destination_reg}, x{source_reg}, {shift_amount}  (Shift Right Logical - Immediate)")
                pass

            # --- Instruction 'SRAI' ---
            elif shift_instruction_type == 0x20:
                source_reg_value = interpret_as_32_bit_signed_value(source_reg_value)

                # Python's shift operator is arithmetic shift operator so it should automatically sign-extend the value
                result = source_reg_value >> shift_amount

                registers.integer_regs[destination_reg] = result & 0xFFFFFFFF

                logger.register_executed_instruction(f"srai x{destination_reg}, x{source_reg}, {shift_amount}  (Shift Right Arithmeticly - Immediate)")
                pass

            else:
                print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
                quit()
            pass

        # --- Instruction 'ORI' ---
        elif instruction_subtype == 6:

            # This instruction interprets 12-bit immediate as signed value. Before making the logic operation on 32-bit
            # register, we need to "sign extend" the immediate to 32-bit length
            immediate_val = sign_extend_12_bit_value(immediate_val)

            result = source_reg_value | immediate_val

            registers.integer_regs[destination_reg] = result

            logger.register_executed_instruction(f"ori x{destination_reg}, x{source_reg}, {immediate_val}  (bitwise OR - Immediate)")
            pass

        # --- Instruction 'ANDI' ---
        elif instruction_subtype == 7:

            # This instruction interprets 12-bit immediate as signed value. Before making the logic operation on 32-bit
            # register, we need to "sign extend" the immediate to 32-bit length
            immediate_val = sign_extend_12_bit_value(immediate_val)

            result = source_reg_value & immediate_val

            registers.integer_regs[destination_reg] = result

            logger.register_executed_instruction(f"andi x{destination_reg}, x{source_reg}, {immediate_val}  (bitwise AND - Immediate)")
            pass

        else:
            print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
            quit()
        pass

    # --- instruction "AUIPC" ---
    elif opcode == 0x17:

        destination_reg, immediate_val = Instruction_parser.decode_U_type(instruction)

        immediate_val = interpret_as_20_bit_signed_value(immediate_val)

        registers.integer_regs[destination_reg] = registers.instruction_pointer + (immediate_val << 12)

        logger.register_executed_instruction(f"auipc x{destination_reg}, {immediate_val}  (Add Upper Immediate to PC)")
        pass

    # --- 'Store' instructions ---
    elif opcode == 0x23:

        instruction_subtype, source_reg_1, source_reg_2, immediate_val = Instruction_parser.decode_S_type(instruction)

        # Immediate is a signed value for all 'store' instructions
        immediate_val = interpret_as_12_bit_signed_value(immediate_val)

        address = registers.integer_regs[source_reg_1] + immediate_val
        value_to_write = registers.integer_regs[source_reg_2]

        # --- instruction "SB" ---
        if instruction_subtype == 0x0:
            memory.write_1_byte(address, value_to_write & 0xFF)

            logger.register_executed_instruction(f"sw x{source_reg_2}, {immediate_val}(x{source_reg_1})  (Store Byte, 8-bit)")
            pass

        # --- instruction "SH" ---
        elif instruction_subtype == 0x1:
            memory.write_2_bytes__little_endian(address, value_to_write)

            logger.register_executed_instruction(f"sw x{source_reg_2}, {immediate_val}(x{source_reg_1})  (Store Half-word, 16-bit)")
            pass

        # --- instruction "SW" ---
        elif instruction_subtype == 0x2:
            memory.write_4_bytes__little_endian(address, value_to_write)

            logger.register_executed_instruction(f"sw x{source_reg_2}, {immediate_val}(x{source_reg_1})  (Store Word, 32-bit)")
            pass
        else:
            print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
            quit()
        pass

    # --- RV32A Atomic instructions ---
    elif opcode == 0x2f:
        instruction_subtype_f3, instruction_subtype_f5, source_reg_1, source_reg_2, destination_reg = Instruction_parser.decode_R_type_atomic(instruction)

        source_reg_1_val = registers.integer_regs[source_reg_1]
        source_reg_2_val = registers.integer_regs[source_reg_2]

        if instruction_subtype_f3 == 0x2:

            # destination_reg <-- memory(source_reg_1_val)
            old_value_in_memory = memory.get_4_bytes__little_endian(address=source_reg_1_val)
            registers.integer_regs[destination_reg] = old_value_in_memory

            # --- instruction "AMO_ADD.W" ---
            if instruction_subtype_f5 == 0x00:

                new_value_in_memory = old_value_in_memory + source_reg_2_val
                new_value_in_memory = new_value_in_memory & 0xFFFFFFFF # Shorten the value to 32 bits if it's longer than that

                memory.write_4_bytes__little_endian(address=source_reg_1_val, value=new_value_in_memory)

                logger.register_executed_instruction(f"amoadd.w x{destination_reg}, x{source_reg_2}, (x{source_reg_1})  (Atomic ADD)")
                pass

            # --- instruction "LD.W" ---
            elif instruction_subtype_f5 == 0x02:

                address_to_load = registers.integer_regs[source_reg_1]

                value_at_address = memory.get_4_bytes__little_endian(address_to_load)

                registers.atomic_load_reserved__address = address_to_load

                registers.integer_regs[destination_reg] = value_at_address

                logger.register_executed_instruction(f"ld.w x{destination_reg}, x{source_reg_1}  (Load Reserved - Atomic)")
                pass

            # --- instruction "SC.W" ---
            elif instruction_subtype_f5 == 0x03:

                address_to_store = registers.integer_regs[source_reg_1]

                if address_to_store == registers.atomic_load_reserved__address:
                    condition_result = 0

                    value_to_store = registers.integer_regs[source_reg_2]

                    memory.write_4_bytes__little_endian(address_to_store, value_to_store)
                else:
                    condition_result = 1

                registers.atomic_load_reserved__address = -1
                registers.integer_regs[destination_reg] = condition_result

                logger.register_executed_instruction(f"sc.w x{destination_reg}, x{source_reg_2}, (x{source_reg_1})  (Store Conditional - Atomic)")
                pass

            # --- instruction "AMO_OR.W" ---
            elif instruction_subtype_f5 == 0x08:

                # memory(source_reg_1_val) <-- memory(source_reg_1_val) | source_reg_2_val
                new_value_in_memory = old_value_in_memory | source_reg_2_val
                memory.write_4_bytes__little_endian(address=source_reg_1_val, value=new_value_in_memory)

                logger.register_executed_instruction(f"amoor.w x{destination_reg}, x{source_reg_2}, (x{source_reg_1})  (Atomic OR)")
                pass
            else:
                print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
                quit()
            pass
        else:
            print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
            quit()
        pass

    # --- Arithmetic/Logic instructions - registers only ---
    elif opcode == 0x33:
        instruction_subtype_f3, instruction_subtype_f7, source_reg_1, source_reg_2, destination_reg = Instruction_parser.decode_R_type(instruction)

        source_reg_1_val = registers.integer_regs[source_reg_1]
        source_reg_2_val = registers.integer_regs[source_reg_2]

        if instruction_subtype_f7 == 0x0:

            # --- instruction "ADD" ---
            if instruction_subtype_f3 == 0:
                result = source_reg_1_val + source_reg_2_val

                # Make sure that the result is limited to only first 32 bits of the value
                result = result & 0xFFFFFFFF

                registers.integer_regs[destination_reg] = result

                logger.register_executed_instruction(f"add x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Addition)")
                pass

            # --- instruction "SLL" ---
            elif instruction_subtype_f3 == 1:
                value_to_be_shifted = source_reg_1_val
                shift_amount = source_reg_2_val & 0b11111  # Get only the lower 5 bits of the register rs2

                result = value_to_be_shifted << shift_amount

                # Make sure that the result is limited to only first 32 bits of the value
                result = result & 0xFFFFFFFF

                registers.integer_regs[destination_reg] = result

                logger.register_executed_instruction(f"sll x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Shift Left Logical)")
                pass

            # --- instruction "SLTU" ---
            elif instruction_subtype_f3 == 3:

                if source_reg_1_val < source_reg_2_val:
                    result = 1
                else:
                    result = 0

                registers.integer_regs[destination_reg] = result

                logger.register_executed_instruction(f"sltu x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Set Less Than - Unsigned)")
                pass

            # --- instruction "XOR" ---
            elif instruction_subtype_f3 == 4:

                result = source_reg_1_val ^ source_reg_2_val

                registers.integer_regs[destination_reg] = result

                logger.register_executed_instruction(f"xor x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Bitwise XOR)")
                pass

            # --- instruction "SRL" ---
            elif instruction_subtype_f3 == 5:

                value_to_be_shifted = source_reg_1_val
                shift_amount = source_reg_2_val & 0b11111  # Get only the lower 5 bits of the register rs2

                result = value_to_be_shifted >> shift_amount

                registers.integer_regs[destination_reg] = result

                logger.register_executed_instruction(f"srl x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Shift Right Logical)")
                pass

            # --- instruction "OR" ---
            elif instruction_subtype_f3 == 6:

                result = source_reg_1_val | source_reg_2_val

                registers.integer_regs[destination_reg] = result

                logger.register_executed_instruction(f"or x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Bitwise OR)")
                pass

            # --- instruction "AND" ---
            elif instruction_subtype_f3 == 7:

                result = source_reg_1_val & source_reg_2_val

                registers.integer_regs[destination_reg] = result

                logger.register_executed_instruction(f"and x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Bitwise AND)")
                pass
            else:
                print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
                quit()
            pass

        # --- RV32M Multiply Extension ---
        elif instruction_subtype_f7 == 0x1:

            # --- instruction "MUL" ---
            if instruction_subtype_f3 == 0:
                source_reg_1_val = interpret_as_32_bit_signed_value(source_reg_1_val)
                source_reg_2_val = interpret_as_32_bit_signed_value(source_reg_2_val)

                result = source_reg_1_val * source_reg_2_val

                # Shorten the result to 32-bits
                result = result & 0xFFFFFFFF

                registers.integer_regs[destination_reg] = result

                logger.register_executed_instruction(f"mul x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Signed Multiplication )")

            # --- instruction "MULH" ---
            elif instruction_subtype_f3 == 1:
                source_reg_1_val = interpret_as_32_bit_signed_value(source_reg_1_val)
                source_reg_2_val = interpret_as_32_bit_signed_value(source_reg_2_val)

                result = source_reg_1_val * source_reg_2_val

                # Multiplication of two 32-bit numbers can result in a much larger number.
                # Get only the bits higher than 32 bits (0xFFFFFFFF00000000)
                result = (result >> 32) & 0xFFFFFFFF

                registers.integer_regs[destination_reg] = result

                logger.register_executed_instruction(f"mulh x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Signed Multiplication - Higher-order bits)")

            # --- instruction "MULHU" ---
            elif instruction_subtype_f3 == 3:
                result = source_reg_1_val * source_reg_2_val

                # Multiplication of two 32-bit numbers can result in a much larger number.
                # Get only the bits higher than 32 bits (0xFFFFFFFF00000000)
                result = (result >> 32) & 0xFFFFFFFF

                registers.integer_regs[destination_reg] = result

                logger.register_executed_instruction(f"mulhu x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Unsigned Multiplication - Higher-order bits)")

            # --- instruction "DIV" ---
            elif instruction_subtype_f3 == 4:
                dividend = interpret_as_32_bit_signed_value(source_reg_1_val)
                divisor  = interpret_as_32_bit_signed_value(source_reg_2_val)

                # TODO1: Handle division by zero
                # TODO2: Handle signed overflow
                result = dividend // divisor

                # TODO: Could I just replace convert_to_32_bit_unsigned_value() with (result & 0xFFFFFFFF)??
                registers.integer_regs[destination_reg] = convert_to_32_bit_unsigned_value(result)

                logger.register_executed_instruction(f"div x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Division - Signed)")
                pass

            # --- instruction "DIVU" ---
            elif instruction_subtype_f3 == 5:
                dividend = source_reg_1_val
                divisor  = source_reg_2_val

                # TODO1: Handle division by zero
                result = dividend // divisor

                registers.integer_regs[destination_reg] = result

                logger.register_executed_instruction(f"divu x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Division - Usigned)")
                pass

            # --- instruction "REM" ---
            elif instruction_subtype_f3 == 6:
                dividend = interpret_as_32_bit_signed_value(source_reg_1_val)
                divisor  = interpret_as_32_bit_signed_value(source_reg_2_val)

                # TODO1: Handle division by zero
                # TODO2: Handle signed overflow
                result = dividend % divisor

                # TODO: Could I just replace convert_to_32_bit_unsigned_value() with (result & 0xFFFFFFFF)??
                registers.integer_regs[destination_reg] = convert_to_32_bit_unsigned_value(result)

                logger.register_executed_instruction(f"rem x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Remainder - Signed)")
                pass

            # --- instruction "REMU" ---
            elif instruction_subtype_f3 == 7:
                dividend = source_reg_1_val
                divisor  = source_reg_2_val

                # TODO1: Handle division by zero
                result = dividend % divisor

                registers.integer_regs[destination_reg] = result

                logger.register_executed_instruction(f"remu x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Remainder - Usigned)")
                pass

            else:
                print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
                quit()
            pass

        elif instruction_subtype_f7 == 0x20:

            # --- instruction "SUB" ---
            if instruction_subtype_f3 == 0x0:
                result = source_reg_1_val - source_reg_2_val

                # Make sure that the result is limited to only first 32 bits of the value
                result = result & 0xFFFFFFFF

                registers.integer_regs[destination_reg] = result

                logger.register_executed_instruction(f"sub x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Subtraction )")
                pass

            # --- instruction "SRA" ---
            elif instruction_subtype_f3 == 5:
                value_to_be_shifted = source_reg_1_val
                shift_amount = source_reg_2_val & 0b11111  # Get only the lower 5 bits of the register rs2

                # Python's shift operator is arithmetic shift operator so it should automatically sign-extend the value
                result = value_to_be_shifted >> shift_amount

                registers.integer_regs[destination_reg] = result & 0xFFFFFFFF

                logger.register_executed_instruction(f"sra x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Shift Right Arithmeticly)")
                pass

            else:
                print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
                quit()
            pass

        else:
            print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
            quit()
        pass

    # --- instruction "LUI" ---
    elif opcode == 0x37:

        destination_reg, immediate_val = Instruction_parser.decode_U_type(instruction)

        registers.integer_regs[destination_reg] = (immediate_val << 12)

        logger.register_executed_instruction(f"lui x{destination_reg}, {interpret_as_20_bit_signed_value(immediate_val)}  (Load Upper Immediate)")
        pass

    # --- Branch instructions ---
    elif opcode == 0x63:

        instruction_subtype, source_reg_1, source_reg_2, immediate_val = Instruction_parser.decode_B_type(instruction)

        source_reg_1_value = registers.integer_regs[source_reg_1]
        source_reg_2_value = registers.integer_regs[source_reg_2]

        source_reg_1_value_signed = interpret_as_32_bit_signed_value(source_reg_1_value)
        source_reg_2_value_signed = interpret_as_32_bit_signed_value(source_reg_2_value)

        # The 12-bit B-immediate encodes SIGNED offsets in MULTIPLES of 2, and is added to the
        # current instruction pointer value. The conditional branch range is ±4 KiB.
        jump_offset = interpret_as_12_bit_signed_value(immediate_val)

        # --- instruction "BEQ" ---
        if instruction_subtype == 0:

            if source_reg_1_value_signed == source_reg_2_value_signed:
                registers.instruction_pointer = registers.instruction_pointer + jump_offset
                instruction_pointer_updated = True

            logger.register_executed_instruction(f"beq x{source_reg_1}, x{source_reg_2}, {immediate_val}  (Branch if EQual)")

        # --- instruction "BNE" ---
        elif instruction_subtype == 1:

            if source_reg_1_value_signed != source_reg_2_value_signed:
                registers.instruction_pointer = registers.instruction_pointer + jump_offset
                instruction_pointer_updated = True

            logger.register_executed_instruction(f"bne x{source_reg_1}, x{source_reg_2}, {immediate_val}  (Branch if Not Equal)")

        # --- instruction "BLT" ---
        elif instruction_subtype == 4:

            if source_reg_1_value_signed < source_reg_2_value_signed:
                registers.instruction_pointer = registers.instruction_pointer + jump_offset
                instruction_pointer_updated = True

            logger.register_executed_instruction(f"blt x{source_reg_1}, x{source_reg_2}, {immediate_val}  (Branch if Less Than)")

        # --- instruction "BGE" ---
        elif instruction_subtype == 5:

            if source_reg_1_value_signed >= source_reg_2_value_signed:
                registers.instruction_pointer = registers.instruction_pointer + jump_offset
                instruction_pointer_updated = True

            logger.register_executed_instruction(f"bge x{source_reg_1}, x{source_reg_2}, {immediate_val}  (Branch if Greater than or Equal)")

        # --- instruction "BLTU" ---
        elif instruction_subtype == 6:

            if source_reg_1_value < source_reg_2_value:
                registers.instruction_pointer = registers.instruction_pointer + jump_offset
                instruction_pointer_updated = True

            logger.register_executed_instruction(f"bltu x{source_reg_1}, x{source_reg_2}, {immediate_val}  (Branch if Less Than - Unsigned)")

        # --- instruction "BGEU" ---
        elif instruction_subtype == 7:

            if source_reg_1_value >= source_reg_2_value:
                registers.instruction_pointer = registers.instruction_pointer + jump_offset
                instruction_pointer_updated = True

            logger.register_executed_instruction(f"bge x{source_reg_1}, x{source_reg_2}, {immediate_val}  (Branch if Greater than or Equal - Unsigned)")

        else:
            print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
            quit()
        pass

    # --- instruction "JALR" ---
    elif opcode == 0x67:
        # Instruction_parser.print_I_type_instruction(instruction)

        instruction_subtype, destination_reg, source_reg, immediate_val = Instruction_parser.decode_I_type(instruction)

        # for this instruction the immediate is a signed value
        immediate_val = interpret_as_12_bit_signed_value(immediate_val)

        # Calculate the address of the next instruction in memory after the location of "jal(r)"
        # This is the "link" part of the instruction, and is usually used (after jumping into functions/procedures)
        # to jump back and continue execution of code physically after the location of "jal(r)" instruction
        address_of_next_instruction = registers.instruction_pointer + 4

        # Calculate new instruction address and update the instruction_pointer
        # This is the "jump" part of the instruction
        # jalr instruction calculates new instruction address by adding together
        # immediate value and value from source register
        jump_address = registers.integer_regs[source_reg] + immediate_val

        registers.instruction_pointer = jump_address

        # Destination register must be updated last, in case the instruction uses the same reg as source and destination
        registers.integer_regs[destination_reg] = address_of_next_instruction

        instruction_pointer_updated = True

        logger.register_executed_instruction(f"jalr x{destination_reg}, x{source_reg} + {immediate_val}  (Jump and Link Register)")
        pass

    # --- instruction "JAL" ---
    elif opcode == 0x6f:
        # Instruction_parser.print_J_type_instruction(instruction)

        destination_reg, immediate_val = Instruction_parser.decode_J_type(instruction)

        # for this instruction the immediate is a signed value
        immediate_val = interpret_as_21_bit_signed_value(immediate_val)

        # Calculate the address of the next instruction in memory after the location of "jal(r)"
        # This is the "link" part of the instruction, and is usually used (after jumping into functions/procedures)
        # to jump back and continue execution of code physically after the location of "jal(r)" instruction
        address_of_next_instruction = registers.instruction_pointer + 4

        # Calculate new instruction address and update the instruction_pointer
        # This is the "jump" part of the instruction
        # jal instruction calculates new instruction address by adding together
        # current instruction pointer and the immediate value
        jump_address = registers.instruction_pointer + immediate_val

        registers.instruction_pointer = jump_address
        registers.integer_regs[destination_reg] = address_of_next_instruction

        instruction_pointer_updated = True

        logger.register_executed_instruction(f"jal x{destination_reg}, {immediate_val}  (Jump and Link)")
        pass

    # --- CSR & ECALL/EBREAK instructions ---
    elif opcode == 0x73:
        # Instruction_parser.print_I_type_instruction(instruction)

        instruction_subtype, destination_reg, source_reg, immediate_val = Instruction_parser.decode_I_type(instruction)

        # In immediate field of the instruction an CSR address value is encoded
        CSR_address = immediate_val

        # --- ECALL/EBREAK instructions ---
        if instruction_subtype == 0x0:

            # --- Instruction "EBREAK" ---
            if immediate_val == 1:
                # ebreak is only relevant for debuggers
                # Used by debuggers to cause control to be transferred back to a debugging environment.
                logger.register_executed_instruction(f"ebreak (Ignored instruction)")
                pass
            else:
                print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
                quit()
            pass

        # --- Instruction "CSRRW" ---
        elif instruction_subtype == 0x1:
            registers.integer_regs[destination_reg] = registers.read_from_CSR_register(CSR_address)
            registers.write_to_CSR_register(CSR_address, registers.integer_regs[source_reg])

            logger.register_executed_instruction(f"csrrw x{destination_reg}, {CSR_address:03x}, x{source_reg}  (Control and Status Register Read-Write)")
            pass

        # --- Instruction "CSRRS" ---
        elif instruction_subtype == 0x2:
            old_value = registers.read_from_CSR_register(CSR_address)
            source_reg_value = registers.integer_regs[source_reg]

            new_value = old_value | source_reg_value

            registers.integer_regs[destination_reg] = old_value
            registers.write_to_CSR_register(CSR_address, new_value)

            logger.register_executed_instruction(f"csrrw x{destination_reg}, {CSR_address:03x}, x{source_reg}  (Control and Status Register Read-Set)")
            pass

        # --- Instruction "CSRRC" ---
        elif instruction_subtype == 0x3:
            old_value = registers.read_from_CSR_register(CSR_address)
            source_reg_value = registers.integer_regs[source_reg]

            new_value = old_value & (~source_reg_value)

            registers.integer_regs[destination_reg] = old_value
            registers.write_to_CSR_register(CSR_address, new_value)

            logger.register_executed_instruction(f"csrrc x{destination_reg}, {CSR_address:03x}, x{source_reg}  (Control and Status Register Read-Clear)")
            pass

        # --- Instruction "CSRRWI" ---
        elif instruction_subtype == 0x5:
            # Immediate value is in this case encoded into bit field that
            # usually holds source register number (RS bit field)
            immediate_val = source_reg

            registers.integer_regs[destination_reg] = registers.read_from_CSR_register(CSR_address)
            registers.write_to_CSR_register(CSR_address, immediate_val)

            logger.register_executed_instruction(f"csrrwi x{destination_reg}, {CSR_address:03x}, {immediate_val}  (Control and Status Register Read-Write Immediate)")
            pass

        # --- Instruction "CSRRSI" ---
        elif instruction_subtype == 0x6:
            # Immediate value is in this case encoded into bit field that
            # usually holds source register number (RS bit field)
            immediate_val = source_reg

            old_value = registers.read_from_CSR_register(CSR_address)

            new_value = old_value | immediate_val

            registers.integer_regs[destination_reg] = old_value
            registers.write_to_CSR_register(CSR_address, new_value)

            logger.register_executed_instruction(f"csrrsi x{destination_reg}, {CSR_address:03x}, {immediate_val}  (Control and Status Register Read-Set Immediate)")
            pass

        # --- Instruction "CSRRCI" ---
        elif instruction_subtype == 0x7:
            # Immediate value is in this case encoded into bit field that
            # usually holds source register number (RS bit field)
            immediate_val = source_reg

            old_value = registers.read_from_CSR_register(CSR_address)

            new_value = old_value & (~immediate_val)

            registers.integer_regs[destination_reg] = old_value
            registers.write_to_CSR_register(CSR_address, new_value)

            logger.register_executed_instruction(f"csrrci x{destination_reg}, {CSR_address:03x}, {immediate_val}  (Control and Status Register Read-Clear immediate)")
            pass
        else:
            print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
            quit()
        pass
    else:
        print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
        quit()

    return instruction_pointer_updated
