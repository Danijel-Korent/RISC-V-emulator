#! /usr/bin/env python3

# Implementing RISC-V CPU emulator for RV32IM instruction set (Integer + multiplication/division)

# DOCU:
#   - https://itnext.io/risc-v-instruction-set-cheatsheet-70961b4bbe8
#   - https://en.wikipedia.org/wiki/RISC-V#Design
#   - https://fraserinnovations.com/risc-v/risc-v-instruction-set-explanation/
#   - https://riscv.org/wp-content/uploads/2017/05/riscv-spec-v2.2.pdf

# QUICK REFERENCE
#
# Instuction list     - https://upload.wikimedia.org/wikipedia/commons/f/fe/RV32IMAC_Instruction_Set.svg
# Instruction format  - https://miro.medium.com/v2/resize:fit:4800/format:webp/1*Mznpgo4kFWIayagpftLmTg.png
# Instruction opcodes - https://www.cs.sfu.ca/~ashriram/Courses/CS295/assets/notebooks/RISCV/RISCV_CARD.pdf
# Instruction decoder - https://luplab.gitlab.io/rvcodecjs
# ISA Manual          - https://five-embeddev.com/riscv-isa-manual/latest/csr.html


from instruction_decoder import get_instruction_destination__register_rd, get_instruction_source_register__rs1, \
                                get_instruction_subtype__funct3, get_instruction_hardcoded_number__immediate_j, \
                                get_instruction_hardcoded_number__immediate_i


# The first 128 bytes of the Linux kernel code
linux_code = [
    111,   0, 192,   5,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
     80,  87,  55,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
      2,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
     82,  73,  83,  67,  86,   0,   0,   0,  82,  83,  67,   5,   0,   0,   0,   0,
     23,  37,   0,   0,  19,   5, 197, 199, 115,  16,  85,  48, 115,  16,   0,  52,
    103, 128,   0,   0, 115,   0,  80,  16, 111, 240, 223, 255, 115,  16,  64,  48,
    115,  16,  64,  52,  15,  16,   0,   0, 239,   0, 128,  10,  23,   5,   0,   0,
     19,   5, 197,   1, 115,  16,  85,  48,  19,   5, 240, 255, 115,  16,   5,  59
]


class CPU_state:
    def __init__(self):
        # All CPUs have one register that holds the address of the next instruction to execute
        # Here we also set the initial instruction address. Normal system would have ROM/flash memory (with initial
        # hardcoded bootloader) mapped into this address. We mapped at this address (a small chunk of) Linux kernel code
        self.instruction_pointer_register = 0x80000000

        # An array of registers
        # RISC-V has 32 integer registers
        self.integer_registers = [0] * 32

# Return one byte value at specified address
# Currently RAM is not implemented at all, only the Linux kernel code at 0x80000000
def read_memory(address):
    if address >= 0x80000000:
        image_addr = address - 0x80000000
        return linux_code[image_addr]

    return 0


def read_32_bits_from_memory__little_endian(address):
    byte0 = read_memory(address)
    byte1 = read_memory(address + 1)
    byte2 = read_memory(address + 2)
    byte3 = read_memory(address + 3)

    value = (byte3 << 24) + (byte2 << 16) + (byte1 << 8) + byte0

    return value


def execute_single_CPU_instruction(cpu_state):
    global Instruction_pointer_register

    print(f"PC: {hex(cpu_state.instruction_pointer_register)}")

    instruction = read_32_bits_from_memory__little_endian(cpu_state.instruction_pointer_register)

    opcode = instruction & 0b01111111

    if opcode == 0x6f: # jal
        print_J_type_instruction(instruction)

        rd = get_instruction_destination__register_rd(instruction)

        immediate_val = get_instruction_hardcoded_number__immediate_j(instruction)
        cpu_state.integer_registers[rd] = cpu_state.instruction_pointer_register + 4

        cpu_state.instruction_pointer_register = cpu_state.instruction_pointer_register + immediate_val
        pass
    else:
        print(f"[ERROR] Instruction not implemented: {hex(instruction)}")
        quit()
    pass


def print_I_type_instruction(instruction):
    opcode = instruction & 0b000000001111111
    rd = get_instruction_destination__register_rd(instruction)
    funct3 = get_instruction_subtype__funct3(instruction)
    rs1 = get_instruction_source_register__rs1(instruction)
    imm = get_instruction_hardcoded_number__immediate_i(instruction)

    print(f"Parsing I-type values from: {hex(instruction)}")
    print(f"  Opcode: {hex(opcode)}")
    print(f"  rd:     {hex(rd)}")
    print(f"  funct3: {hex(funct3)} \n")
    print(f"  rs1:     {hex(rs1)} \n")
    print(f"  imm:    {hex(imm)} \n")
    pass

def print_J_type_instruction(instruction):
    opcode = instruction & 0b000000001111111
    rd = get_instruction_destination__register_rd(instruction)
    imm = get_instruction_hardcoded_number__immediate_j(instruction)

    print(f"Parsing I-type values from instruction: {hex(instruction)}")
    print(f"  Opcode: {hex(opcode)}")
    print(f"  rd:     {hex(rd)}")
    print(f"  imm:    {hex(imm)} \n")
    pass


def emulate_cpu():

    cpu_state = CPU_state()
    while True:
        execute_single_CPU_instruction(cpu_state)
    pass


if __name__ == '__main__':
    emulate_cpu()
