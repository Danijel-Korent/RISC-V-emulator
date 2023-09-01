from helper_functions import interpret_as_32_bit_signed_value, interpret_as_12_bit_signed_value, \
    interpret_as_20_bit_signed_value, interpret_as_21_bit_signed_value, convert_to_32_bit_unsigned_value
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

        # --- Instruction 'LW' ---
        if instruction_subtype == 0x02:
            value = memory.get_4_bytes__little_endian(address)

            registers.integer_regs[destination_reg] = value

            logger.register_executed_instruction(f"lw x{destination_reg}, {immediate_val}(x{source_reg})  (Load Word)")

        # --- Instruction 'LBU' ---
        elif instruction_subtype == 0x04:
            value = memory.get_1_byte(address)

            registers.integer_regs[destination_reg] = value

            logger.register_executed_instruction(f"lbu x{destination_reg}, {immediate_val}(x{source_reg})  (Load Byte - Unsigned)")
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
            shift_amount = immediate_val

            registers.integer_regs[destination_reg] = value_to_be_shifted << shift_amount

            logger.register_executed_instruction(f"slli x{destination_reg}, x{source_reg}, {immediate_val}  (Shift Left Logical - Immediate)")
            pass

        # --- Instruction 'ANDI' ---
        elif instruction_subtype == 7:

            registers.integer_regs[destination_reg] = source_reg_value & immediate_val

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

            logger.register_executed_instruction(f"sw x{source_reg_2}, {immediate_val}(x{source_reg_1})  (Store Byte)")
            pass

        # --- instruction "SW" ---
        elif instruction_subtype == 0x2:
            memory.write_4_bytes__little_endian(address, value_to_write)

            logger.register_executed_instruction(f"sw x{source_reg_2}, {immediate_val}(x{source_reg_1})  (Store Word)")
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
                shift_amount = source_reg_2_val

                registers.integer_regs[destination_reg] = value_to_be_shifted << shift_amount

                logger.register_executed_instruction(f"sll x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Shift Left Logical)")
                pass

            # --- instruction "SLTU" ---
            elif instruction_subtype_f3 == 3:

                if source_reg_1_val < source_reg_2_val:
                    result = 1
                else:
                    result = 0

                registers.integer_regs[destination_reg] = result

                logger.register_executed_instruction(f"slt x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Set Less Than - Unsigned)")
                pass

            # --- instruction "XOR" ---
            elif instruction_subtype_f3 == 4:

                result = source_reg_1_val ^ source_reg_2_val

                registers.integer_regs[destination_reg] = result

                logger.register_executed_instruction(f"xor x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Bitwise XOR)")
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

            # --- instruction "MULHU" ---
            elif instruction_subtype_f3 == 3:
                result = source_reg_1_val * source_reg_2_val

                # Multiplication of two 32-bit numbers can result in a much larger number.
                # Get only the bits higher than 32 bits (0xFFFFFFFF00000000)
                result = result >> 32

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

                logger.register_executed_instruction(f"div x{destination_reg}, x{source_reg_1}, x{source_reg_2}  (Signed Division)")
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

            logger.register_executed_instruction(f"beq x{source_reg_1}, x{source_reg_2}, {immediate_val}  (Branch if EQual")

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

    # --- CSR instructions ---
    elif opcode == 0x73:
        # Instruction_parser.print_I_type_instruction(instruction)

        instruction_subtype, destination_reg, source_reg, immediate_val = Instruction_parser.decode_I_type(instruction)

        # In immediate field of the instruction an CSR address value is encoded
        CSR_address = immediate_val

        # --- Instruction "CSRRW" ---
        if instruction_subtype == 0x1:
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
