#! /usr/bin/env python3

# Implementing RISC-V CPU emulator - only RV32IM instruction set (32-bit integer + multiplication/division)


# The first 128 bytes of the compiled Linux kernel code. Linux kernel code compiles into instructions and data,
# so the array contains instructions with some data here and there
linux_instructions = [
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
        # hardcoded bootloader) mapped into this address. We mapped at this address (a small chunk of) Linux kernel
        self.instruction_pointer_register = 0x80000000

        # An array of registers
        # RISC-V has 32 integer registers
        # https://en.wikipedia.org/wiki/RISC-V#Register_sets
        self.integer_registers = [
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                 ]


class Memory:
    def __init__(self, linux_image):
        self.linux_instructions = linux_image

    # Returns a value stored at specified address
    # WARNING:
    #   Currently RAM is not implemented at all. Only the Linux kernel code at 0x80000000 is accessible. Everything else
    #   just returns zero.
    def get_1_byte(self, address):
        if address >= 0x80000000:
            image_addr = address - 0x80000000
            return self.linux_instructions[image_addr]

        return 0


def execute_single_CPU_instruction(cpu_state, memory):

    print(f"Instruction pointer: {hex(cpu_state.instruction_pointer_register)}")

    print(f"\n[ERROR] Instruction not implemented")
    quit()


def emulate_cpu():

    cpu_state = CPU_state()
    memory = Memory(linux_instructions)

    while True:
        execute_single_CPU_instruction(cpu_state, memory)


# Main starting point of this program/script
if __name__ == '__main__':
    emulate_cpu()
