from helper_functions import interpret_as_32_bit_signed_value, interpret_as_12_bit_signed_value, \
    interpret_as_21_bit_signed_value
from instruction_decoder import Instruction_parser


def execute_instruction(registers, memory, instruction, logger):

    # Extract the 'operation/instruction' type
    opcode = instruction & 0b01111111

    instruction_pointer_updated = False

    # --- Instruction 'LW' ---
    if opcode == 0x03:
        instruction_subtype, destination_reg, source_reg, immediate_val = Instruction_parser.decode_I_type(instruction)

        if instruction_subtype == 0x02:
            base_address = registers.integer_regs[source_reg]
            offset = interpret_as_12_bit_signed_value(immediate_val)

            address = base_address + offset

            value = memory.get_4_bytes__little_endian(address)

            registers.integer_regs[destination_reg] = value

            logger.register_executed_instruction(f"lw x{destination_reg}, {immediate_val}(x{source_reg})  (Load Word)")
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

        # --- Instruction 'ADDI' ---
        if instruction_subtype == 0x0:
            sign = ""

            # The first bit (MSB) tells if the values is negative or not
            # If the first bit of the value is set to 1, then the values is negative, encoded as Two's_complement
            # https://en.wikipedia.org/wiki/Two's_complement
            if (immediate_val & 0b100000000000) == 0:
                registers.integer_regs[destination_reg] = registers.integer_regs[source_reg] + immediate_val
            else:
                immediate_val = (~immediate_val & 0xFFF) + 1
                registers.integer_regs[destination_reg] = registers.integer_regs[source_reg] - immediate_val
                sign = "-"

            # Shorten the register value to 32 bits if it's longer than that after add/sub
            registers.integer_regs[destination_reg] = registers.integer_regs[destination_reg] & 0xFFFFFFFF

            logger.register_executed_instruction(f"addi x{destination_reg}, x{source_reg}, {sign}{immediate_val}  (Add immediate)")
            pass
        else:
            print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
            quit()
        pass

    # --- instruction "AUIPC" ---
    elif opcode == 0x17:

        destination_reg, immediate_val = Instruction_parser.decode_U_type(instruction)

        registers.integer_regs[destination_reg] = registers.instruction_pointer + (immediate_val << 12)

        logger.register_executed_instruction(f"auipc x{destination_reg}, {immediate_val}  (Add Upper Immediate to PC)")
        pass

    # --- instruction "SW" ---
    elif opcode == 0x23:

        instruction_subtype, source_reg_1, source_reg_2, immediate_val = Instruction_parser.decode_S_type(instruction)

        address = registers.integer_regs[source_reg_1] + immediate_val
        value_to_write = registers.integer_regs[source_reg_2]

        memory.write_4_bytes__little_endian(address, value_to_write)

        logger.register_executed_instruction(f"sw x{source_reg_2}, {immediate_val}(x{source_reg_1})  (Store Word)")
        pass

    # --- instruction "LUI" ---
    elif opcode == 0x37:

        destination_reg, immediate_val = Instruction_parser.decode_U_type(instruction)

        registers.integer_regs[destination_reg] = (immediate_val << 12)

        logger.register_executed_instruction(f"lui x{destination_reg}, {immediate_val}  (Load Upper Immediate)")
        pass

    # --- Branch instructions ---
    elif opcode == 0x63:

        instruction_subtype, source_reg_1, source_reg_2, immediate_val = Instruction_parser.decode_B_type(instruction)

        source_reg_1_value = registers.integer_regs[source_reg_1]
        source_reg_2_value = registers.integer_regs[source_reg_2]

        source_reg_1_value = interpret_as_32_bit_signed_value(source_reg_1_value)
        source_reg_2_value = interpret_as_32_bit_signed_value(source_reg_2_value)

        # The 12-bit B-immediate encodes SIGNED offsets in MULTIPLES of 2, and is added to the
        # current instruction pointer value. The conditional branch range is ±4 KiB.
        jump_offset = interpret_as_12_bit_signed_value(immediate_val)

        # --- instruction "BLT" ---
        if instruction_subtype == 0x4:

            if source_reg_1_value < source_reg_2_value:
                registers.instruction_pointer = registers.instruction_pointer + jump_offset
                instruction_pointer_updated = True

            logger.register_executed_instruction(f"blt x{source_reg_1}, x{source_reg_2}, {immediate_val}  (Branch if Less than)")

        # --- instruction "BGE" ---
        elif instruction_subtype == 0x5:

            if source_reg_1_value >= source_reg_2_value:
                registers.instruction_pointer = registers.instruction_pointer + jump_offset
                instruction_pointer_updated = True

            logger.register_executed_instruction(f"bge x{source_reg_1}, x{source_reg_2}, {immediate_val}  (Branch if Greater than or Equal)")
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
            # Immediate values is in this case encoded into bit field that
            # usually holds source register number (RS bit field)
            immediate_val = source_reg

            registers.integer_regs[destination_reg] = registers.read_from_CSR_register(CSR_address)
            registers.write_to_CSR_register(CSR_address, immediate_val)

            logger.register_executed_instruction(f"csrrwi x{destination_reg}, {CSR_address:03x}, {immediate_val}  (Control and Status Register Read-Write Immediate)")
            pass
        else:
            print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
            quit()
        pass
    else:
        print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
        quit()

    return instruction_pointer_updated
