
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
