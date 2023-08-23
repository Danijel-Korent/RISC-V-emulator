from instruction_decoder import Instruction_parser


def execute_instruction(registers, memory, instruction):

    # Extract the 'operation/instruction' type
    opcode = instruction & 0b01111111

    instruction_pointer_updated = False

    # --- Instruction 'FENCE' ---
    if opcode == 0x0f:
        # Fence is only relevant for more complex CPU implementations
        print(f"Ignored instruction -> fence \n")
        pass

    # --- Arithmetic/Logic instructions with immediate ---
    elif opcode == 0x13:
        # Arithmetic/logic instructions with immediate value hardcoded into instruction
        Instruction_parser.print_I_type_instruction(instruction)

        instruction_subtype, destination_reg, source_reg, immediate_val = Instruction_parser.decode_I_type(instruction)

        # --- Instruction 'ADDI' ---
        if instruction_subtype == 0x0:
            registers.integer_regs[destination_reg] = registers.integer_regs[source_reg] + immediate_val

            print(f"Executed instruction -> addi x{destination_reg}, x{source_reg}, {immediate_val}  (Add immediate)\n")
            pass
        else:
            print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
            quit()
        pass

    # --- instruction "AUIPC" ---
    elif opcode == 0x17:

        destination_reg, immediate_val = Instruction_parser.decode_U_type(instruction)

        registers.integer_regs[destination_reg] = registers.instruction_pointer + (immediate_val << 12)

        print(f"Executed instruction -> auipc x{destination_reg}, {immediate_val}  (Add Upper Immediate to PC)\n")
        pass

    # --- instruction "JALR" ---
    elif opcode == 0x67:
        Instruction_parser.print_I_type_instruction(instruction)

        instruction_subtype, destination_reg, source_reg, immediate_val = Instruction_parser.decode_I_type(instruction)

        # instruction address -> destination_register
        registers.integer_regs[destination_reg] = registers.instruction_pointer

        # Calculate new instruction address and update the instruction_pointer
        # jarl instruction calculates new instruction address by adding together
        # immediate value and value from source register
        registers.instruction_pointer = registers.integer_regs[source_reg] + immediate_val

        instruction_pointer_updated = True

        print(f"Executed instruction -> jalr x{destination_reg}, x{source_reg} + {immediate_val}  (Jump and Link Register)\n")
        pass

    # --- instruction "JAL" ---
    elif opcode == 0x6f:
        Instruction_parser.print_J_type_instruction(instruction)

        destination_reg, immediate_val = Instruction_parser.decode_J_type(instruction)

        registers.integer_regs[destination_reg] = registers.instruction_pointer + 4

        # Update instruction pointer to a new value
        registers.instruction_pointer = registers.instruction_pointer + immediate_val

        instruction_pointer_updated = True

        print(f"Executed instruction -> jal x{destination_reg}, {immediate_val}  (Jump and Link)\n")
        pass

    # --- CSR instructions ---
    elif opcode == 0x73:
        Instruction_parser.print_I_type_instruction(instruction)

        instruction_subtype, destination_reg, source_reg, immediate_val = Instruction_parser.decode_I_type(instruction)

        # In immediate field of the instruction an CSR address value is encoded
        CSR_address = immediate_val

        # --- Instruction "CSRRW" ---
        if instruction_subtype == 0x1:
            registers.integer_regs[destination_reg] = registers.read_from_CSR_register(CSR_address)
            registers.write_to_CSR_register(CSR_address, registers.integer_regs[source_reg])

            print(f"Executed instruction -> csrrw x{destination_reg}, {CSR_address}, x{source_reg}  (Control and Status Register Read-Write)\n")
            pass

        # --- Instruction "CSRRWI" ---
        elif instruction_subtype == 0x5:
            # Immediate values is in this case encoded into bit field that
            # usually holds source register number (RS bit field)
            immediate_val = source_reg

            registers.integer_regs[destination_reg] = registers.read_from_CSR_register(CSR_address)
            registers.write_to_CSR_register(CSR_address, immediate_val)

            print(f"Executed instruction -> csrrwi x{destination_reg}, {CSR_address}, {immediate_val}  (Control and Status Register Read-Write Immediate)\n")
            pass
        else:
            print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
            quit()
        pass
    else:
        print(f"[ERROR] Instruction not implemented: 0x{instruction:08x} !!")
        quit()

    return instruction_pointer_updated
