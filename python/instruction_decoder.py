
# DOCU:
#   - https://itnext.io/risc-v-instruction-set-cheatsheet-70961b4bbe8
#   - https://en.wikipedia.org/wiki/RISC-V#Design
#   - https://fraserinnovations.com/risc-v/risc-v-instruction-set-explanation/
#   - https://book.rvemu.app/instruction-set/01-rv64i.html
#   - https://riscv.org/wp-content/uploads/2017/05/riscv-spec-v2.2.pdf

# QUICK REFERENCE
#
# RISC-V Reference card (formats, opcodes, lists, registers)
#
#   - https://www.cs.sfu.ca/~ashriram/Courses/CS295/assets/notebooks/RISCV/RISCV_CARD.pdf
#   - https://book.rvemu.app/img/2-1-1.png
#
# Instruction list    - https://upload.wikimedia.org/wikipedia/commons/f/fe/RV32IMAC_Instruction_Set.svg
# Instruction format  - https://miro.medium.com/v2/resize:fit:4800/format:webp/1*Mznpgo4kFWIayagpftLmTg.png
# Instruction opcodes - https://www.cs.sfu.ca/~ashriram/Courses/CS295/assets/notebooks/RISCV/RISCV_CARD.pdf
# Instruction decoder - https://luplab.gitlab.io/rvcodecjs
# ISA Manual          - https://five-embeddev.com/riscv-isa-manual/latest/csr.html

class Instruction_parser:

    @staticmethod
    def decode_I_type(instruction):
        instruction_subtype = Instruction_parser.get_subtype__funct3(instruction)
        destination_reg     = Instruction_parser.get_destination_register__rd(instruction)
        source_reg          = Instruction_parser.get_source_register__rs1(instruction)
        immediate_val       = Instruction_parser.get_hardcoded_number__immediate_i(instruction)

        return instruction_subtype, destination_reg, source_reg, immediate_val

    @staticmethod
    def decode_J_type(instruction):
        #                   imm[20]      imm[10:1]                imm[11]       imm[19:12]           rd (dest reg)                 opcode
        # Instruction bit no. | 31 | 30 29 28 27 26 25 24 23 22 21 | 20 | 19 18 17 16 15 14 13 12 | 11 10 09 08 07 | 06 05 04 03 02 01 00
        # Immediate   bit no. | 20 | 10 09 08 07 06 05 04 03 02 01 | 11 | 19 18 17 16 15 14 13 12 | rd rd rd rd rd | op op op op op op op

        destination_reg = Instruction_parser.get_destination_register__rd(instruction)
        immediate_val   = Instruction_parser.get_hardcoded_number__immediate_j(instruction)

        return destination_reg, immediate_val

    @staticmethod
    def decode_U_type(instruction):
        destination_reg = Instruction_parser.get_destination_register__rd(instruction)
        immediate_val   = Instruction_parser.get_hardcoded_number__immediate_u(instruction)

        return destination_reg, immediate_val

    @staticmethod
    def decode_B_type(instruction):
        #                    imm[12]        imm[10:5]            rs2              rs1          funct3     imm[4:1]   imm[11]              opcode
        # Instruction bit no. |  31   | 30 29 28 27 26 25 | 24 23 22 21 20 | 19 18 17 16 15 | 14 13 12 | 11 10 09 08 | 07 | 06 05 04 03 02 01 00
        # Immediate   bit no. |  12   | 10 09 08 07 06 05 | s2 s2 s2 s2 s2 | s1 s1 s1 s1 s1 | f3 f3 f3 | 04 03 02 01 | 11 | op op op op op op op

        instruction_subtype = Instruction_parser.get_subtype__funct3(instruction)
        source_reg_1        = Instruction_parser.get_source_register__rs1(instruction)
        source_reg_2        = Instruction_parser.get_source_register__rs2(instruction)
        immediate_val       = Instruction_parser.get_hardcoded_number__immediate_b(instruction)

        return instruction_subtype, source_reg_1, source_reg_2, immediate_val

    @staticmethod
    def decode_S_type(instruction):
        #                             imm[11:5]              rs2              rs1          funct3       imm[4:0]                    opcode
        # Instruction bit no. |  31 30 29 28 27 26 25 | 24 23 22 21 20 | 19 18 17 16 15 | 14 13 12 | 11 10 09 08 07 | 06 05 04 03 02 01 00
        # Immediate   bit no. |  11 10 09 08 07 06 05 | s2 s2 s2 s2 s2 | s1 s1 s1 s1 s1 | f3 f3 f3 | 04 03 02 01 00 | op op op op op op op

        instruction_subtype = Instruction_parser.get_subtype__funct3(instruction)
        source_reg_1        = Instruction_parser.get_source_register__rs1(instruction)
        source_reg_2        = Instruction_parser.get_source_register__rs2(instruction)
        immediate_val       = Instruction_parser.get_hardcoded_number__immediate_s(instruction)

        return instruction_subtype, source_reg_1, source_reg_2, immediate_val

    @staticmethod
    def get_subtype__funct3(instruction):
        val = instruction & 0b00000000000000000111000000000000
        val = val >> 12
        return val

    @staticmethod
    def get_source_register__rs1(instruction):
        val = instruction & 0b00000000000011111000000000000000
        return val >> 15

    @staticmethod
    def get_source_register__rs2(instruction):
        val = instruction & 0b00000001111100000000000000000000
        return val >> 20

    @staticmethod
    def get_destination_register__rd(instruction):
        val = instruction & 0b00000000000000000000111110000000
        val = val >> 7
        return val

    @staticmethod
    def get_hardcoded_number__immediate_i(instruction):
        # val = instruction & 0b11111111111100000000000000000000 <- Unnecessary
        val = instruction >> 20
        return val

    @staticmethod
    def get_hardcoded_number__immediate_u(instruction):
        # val = instruction & 0b11111111111111111111000000000000 <- Unnecessary
        val = instruction >> 12
        return val

    @staticmethod
    def get_hardcoded_number__immediate_j(instruction):
        # Bits Instruction -> Immediate
        #                   imm[20]      imm[10:1]                imm[11]       imm[19:12]           rd (dest reg)                 opcode
        # Instruction bit no. | 31 | 30 29 28 27 26 25 24 23 22 21 | 20 | 19 18 17 16 15 14 13 12 | 11 10 09 08 07 | 06 05 04 03 02 01 00
        # Immediate   bit no. | 20 | 10 09 08 07 06 05 04 03 02 01 | 11 | 19 18 17 16 15 14 13 12 | rd rd rd rd rd | op op op op op op op

        # Bits Immediate -> Instruction
        #                   imm[20]         imm[19:12]       imm[11]          imm[10:1]             Always zero
        # Immediate   bit no. | 20 | 19 18 17 16 15 14 13 12 | 11 | 10 09 08 07 06 05 04 03 02 01 | 00  |
        # Instruction bit no. | 31 | 19 18 17 16 15 14 13 12 | 20 | 30 29 28 27 26 25 24 23 22 21 | n/a |

        instruction_bits_31_31 = instruction & 0b10000000000000000000000000000000
        instruction_bits_30_21 = instruction & 0b01111111111000000000000000000000
        instruction_bits_20_20 = instruction & 0b00000000000100000000000000000000
        instruction_bits_19_12 = instruction & 0b00000000000011111111000000000000

        immediate_bits_20_20 = instruction_bits_31_31 >> 11
        immediate_bits_19_12 = instruction_bits_19_12
        immediate_bits_11_11 = instruction_bits_20_20 >> 9
        immediate_bits_10_01 = instruction_bits_30_21 >> 20
        immediate_bits_00_00 = 0

        val = immediate_bits_20_20 | immediate_bits_19_12 | immediate_bits_11_11 | immediate_bits_10_01 | immediate_bits_00_00

        return val

    @staticmethod
    def get_hardcoded_number__immediate_b(instruction):

        # Bits Instruction -> Immediate
        #                    imm[12]        imm[10:5]            rs2              rs1          funct3     imm[4:1]   imm[11]              opcode
        # Instruction bit no. |  31   | 30 29 28 27 26 25 | 24 23 22 21 20 | 19 18 17 16 15 | 14 13 12 | 11 10 09 08 | 07 | 06 05 04 03 02 01 00
        # Immediate   bit no. |  12   | 10 09 08 07 06 05 | s2 s2 s2 s2 s2 | s1 s1 s1 s1 s1 | f3 f3 f3 | 04 03 02 01 | 11 | op op op op op op op

        # Bits Immediate -> Instruction
        #                    imm[12]  imm[11]    imm[10:5]         imm[4:1]    Always zero
        # Immediate   bit no. |  12   | 11 | 10 09 08 07 06 05 | 04 03 02 01 | 00  |
        # Instruction bit no. |  31   | 07 | 30 29 28 27 26 25 | 11 10 09 08 | n/a |

        instruction_bits_31_31 = instruction & 0b10000000000000000000000000000000
        instruction_bits_30_25 = instruction & 0b01111110000000000000000000000000
        instruction_bits_11_08 = instruction & 0b00000000000000000000111100000000
        instruction_bits_07_07 = instruction & 0b00000000000000000000000010000000

        immediate_bits_12_12 = instruction_bits_31_31 >> 19
        immediate_bits_11_11 = instruction_bits_07_07 << 4
        immediate_bits_10_05 = instruction_bits_30_25 >> 20
        immediate_bits_04_01 = instruction_bits_11_08 >> 7
        immediate_bits_00_00 = 0

        val = immediate_bits_12_12 | immediate_bits_11_11 | immediate_bits_10_05 | immediate_bits_04_01 | immediate_bits_00_00

        return val

    @staticmethod
    def get_hardcoded_number__immediate_s(instruction):

        # Bits Instruction -> Immediate
        #                             imm[11:5]              rs2              rs1          funct3       imm[4:0]                    opcode
        # Instruction bit no. |  31 30 29 28 27 26 25 | 24 23 22 21 20 | 19 18 17 16 15 | 14 13 12 | 11 10 09 08 07 | 06 05 04 03 02 01 00
        # Immediate   bit no. |  11 10 09 08 07 06 05 | s2 s2 s2 s2 s2 | s1 s1 s1 s1 s1 | f3 f3 f3 | 04 03 02 01 00 | op op op op op op op

        # Bits Immediate -> Instruction
        #                             imm[11:5]            imm[4:0]
        # Immediate   bit no. |  11 10 09 08 07 06 05 | 04 03 02 01 00 |
        # Instruction bit no. |  31 30 29 28 27 26 25 | 11 10 09 08 07 |

        instruction_bits_31_25 = instruction & 0b11111110000000000000000000000000
        instruction_bits_11_07 = instruction & 0b00000000000000000000111110000000

        immediate_bits_11_05 = instruction_bits_31_25 >> 20
        immediate_bits_04_00 = instruction_bits_11_07 >> 7

        val = immediate_bits_11_05 | immediate_bits_04_00

        return val

    @staticmethod
    def print_J_type_instruction(instruction):
        opcode = instruction & 0b00000000000000000000000001111111
        rd = Instruction_parser.get_destination_register__rd(instruction)
        imm = Instruction_parser.get_hardcoded_number__immediate_j(instruction)

        destination_reg, immediate_val = Instruction_parser.decode_J_type(instruction)

        print(f"Parsing I-type values from instruction: 0x{instruction:08x}")
        print(f"  Opcode:           {hex(opcode)}")
        print(f"  Destination reg.: {hex(destination_reg)}")
        print(f"  Immediate value:  {hex(immediate_val)} \n")
        pass

    @staticmethod
    def print_I_type_instruction(instruction):
        opcode = instruction & 0b00000000000000000000000001111111

        instruction_subtype, destination_reg, source_reg, immediate_val = Instruction_parser.decode_I_type(instruction)

        print(f"Parsing I-type values from instruction: 0x{instruction:08x}")
        print(f"  Opcode:           {hex(opcode)}")
        print(f"  Opcode subtype:   {hex(instruction_subtype)}")
        print(f"  Source reg.:      {hex(source_reg)}")
        print(f"  Destination reg.: {hex(destination_reg)}")
        print(f"  Immediate value:  {hex(immediate_val)} \n")
        pass


if __name__ == '__main__':
    print(f"\nExecuting:\n\t{__file__} \n")
    print("Hopefully here we will have tests for functions in this file")
