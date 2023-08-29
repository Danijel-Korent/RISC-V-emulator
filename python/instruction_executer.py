from helper_functions import interpret_as_32_bit_signed_value, interpret_as_12_bit_signed_value
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

            logger.register_executed_instruction(f"Executed instruction -> lw x{destination_reg}, {immediate_val}(x{source_reg})  (Load Word)\n")
        else:
            print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
            quit()
        pass

    # --- Instruction 'FENCE' ---
    elif opcode == 0x0f:
        # Fence is only relevant for more complex CPU implementations
        logger.register_executed_instruction(f"Ignored instruction -> fence \n")
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

            logger.register_executed_instruction(f"Executed instruction -> addi x{destination_reg}, x{source_reg}, {sign}{immediate_val}  (Add immediate)\n")
            pass
        else:
            print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
            quit()
        pass

    # --- instruction "AUIPC" ---
    elif opcode == 0x17:

        destination_reg, immediate_val = Instruction_parser.decode_U_type(instruction)

        registers.integer_regs[destination_reg] = registers.instruction_pointer + (immediate_val << 12)

        logger.register_executed_instruction(f"Executed instruction -> auipc x{destination_reg}, {immediate_val}  (Add Upper Immediate to PC)\n")
        pass

    # --- instruction "SW" ---
    elif opcode == 0x23:

        instruction_subtype, source_reg_1, source_reg_2, immediate_val = Instruction_parser.decode_S_type(instruction)

        address = registers.integer_regs[source_reg_1] + immediate_val
        value_to_write = registers.integer_regs[source_reg_2]

        memory.write_1_byte(address, value_to_write)

        logger.register_executed_instruction(f"Executed instruction -> sw x{source_reg_2}, {immediate_val}(x{source_reg_1})  (Store Word)\n")
        pass

    # --- instruction "LUI" ---
    elif opcode == 0x37:

        destination_reg, immediate_val = Instruction_parser.decode_U_type(instruction)

        registers.integer_regs[destination_reg] = (immediate_val << 12)

        logger.register_executed_instruction(f"Executed instruction -> lui x{destination_reg}, {immediate_val}  (Load Upper Immediate)\n")
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

            logger.register_executed_instruction(f"Executed instruction -> blt x{source_reg_1}, x{source_reg_2}, {immediate_val}  (Branch if Less than)\n")

        # --- instruction "BGE" ---
        elif instruction_subtype == 0x5:

            if source_reg_1_value >= source_reg_2_value:
                registers.instruction_pointer = registers.instruction_pointer + jump_offset
                instruction_pointer_updated = True

            logger.register_executed_instruction(f"Executed instruction -> bge x{source_reg_1}, x{source_reg_2}, {immediate_val}  (Branch if Greater than or Equal)\n")
        else:
            print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
            quit()
        pass

    # --- instruction "JALR" ---
    elif opcode == 0x67:
        # Instruction_parser.print_I_type_instruction(instruction)

        instruction_subtype, destination_reg, source_reg, immediate_val = Instruction_parser.decode_I_type(instruction)

        # Calculate new instruction address and update the instruction_pointer
        # jarl instruction calculates new instruction address by adding together
        # immediate value and value from source register
        registers.instruction_pointer = registers.integer_regs[source_reg] + immediate_val

        # instruction address -> destination_register
        # Destination register must be updated last, in case source_reg and destination_reg are the same
        registers.integer_regs[destination_reg] = registers.instruction_pointer

        instruction_pointer_updated = True

        logger.register_executed_instruction(f"Executed instruction -> jalr x{destination_reg}, x{source_reg} + {immediate_val}  (Jump and Link Register)\n")
        pass

    # --- instruction "JAL" ---
    elif opcode == 0x6f:
        # Instruction_parser.print_J_type_instruction(instruction)

        destination_reg, immediate_val = Instruction_parser.decode_J_type(instruction)

        registers.integer_regs[destination_reg] = registers.instruction_pointer + 4

        # Update instruction pointer to a new value
        registers.instruction_pointer = registers.instruction_pointer + immediate_val

        instruction_pointer_updated = True

        logger.register_executed_instruction(f"Executed instruction -> jal x{destination_reg}, {immediate_val}  (Jump and Link)\n")
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

            logger.register_executed_instruction(f"Executed instruction -> csrrw x{destination_reg}, {CSR_address:03x}, x{source_reg}  (Control and Status Register Read-Write)\n")
            pass

        # --- Instruction "CSRRS" ---
        elif instruction_subtype == 0x2:
            old_value = registers.read_from_CSR_register(CSR_address)
            source_reg_value = registers.integer_regs[source_reg]

            new_value = old_value | source_reg_value

            registers.integer_regs[destination_reg] = old_value
            registers.write_to_CSR_register(CSR_address, new_value)

            logger.register_executed_instruction(f"Executed instruction -> csrrw x{destination_reg}, {CSR_address:03x}, x{source_reg}  (Control and Status Register Read-Set)\n")
            pass

        # --- Instruction "CSRRC" ---
        elif instruction_subtype == 0x3:
            old_value = registers.read_from_CSR_register(CSR_address)
            source_reg_value = registers.integer_regs[source_reg]

            new_value = old_value & (~source_reg_value)

            registers.integer_regs[destination_reg] = old_value
            registers.write_to_CSR_register(CSR_address, new_value)

            logger.register_executed_instruction(f"Executed instruction -> csrrc x{destination_reg}, {CSR_address:03x}, x{source_reg}  (Control and Status Register Read-Clear)\n")
            pass

        # --- Instruction "CSRRWI" ---
        elif instruction_subtype == 0x5:
            # Immediate values is in this case encoded into bit field that
            # usually holds source register number (RS bit field)
            immediate_val = source_reg

            registers.integer_regs[destination_reg] = registers.read_from_CSR_register(CSR_address)
            registers.write_to_CSR_register(CSR_address, immediate_val)

            logger.register_executed_instruction(f"Executed instruction -> csrrwi x{destination_reg}, {CSR_address:03x}, {immediate_val}  (Control and Status Register Read-Write Immediate)\n")
            pass
        else:
            print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
            quit()
        pass
    else:
        print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
        quit()

    return instruction_pointer_updated
