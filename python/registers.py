

class Registers:
    def __init__(self):
        # All CPUs have one register that holds the address of the next instruction to execute
        # Here we also set the initial instruction address. Normal system would have ROM/flash memory (with initial
        # hardcoded bootloader) mapped into this address. We mapped at this address (a small chunk of) Linux kernel
        self.instruction_pointer = 0x80000000

        # An array of registers
        # RISC-V has 32 integer registers
        # https://en.wikipedia.org/wiki/RISC-V#Register_sets
        self.integer_regs = [
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                 ]

        self.CSR_mscratch = 0

    def print_register_values(self):
        # just to shorten the variable name
        reg = self.integer_regs

        for i in range(8):
            offset = i*4
            for x in range(4):
                reg_no = offset + x
                print(f"x{reg_no:02}: {reg[reg_no]:08x}, ", end='')
            # just for new line
            print("")

    def read_from_CSR_register(self, register_num):
        if register_num == 0x304:
            print(f"Tried to read CSR[0x{register_num:x}]  (register 'mie': Machine Interrupt Enable) \n")
        elif register_num == 0x340:
            print(f"Tried to read CSR[0x{register_num:x}]  (register 'mscratch': Scratch register) \n")
            return self.CSR_mscratch
        elif register_num == 0x344:
            print(f"Tried to read CSR[0x{register_num:x}]  (register 'mip': Machine Interrupt Pending) \n")
        else:
            print(f"[ERROR] Tried to read unknown CSR register -> CSR[0x{register_num:x}] \n")
            exit()
        return 0

    def write_to_CSR_register(self, register_num, value):
        if register_num == 0x304:
            print(f"Tried to write CSR[0x{register_num:x}] = 0x{value:x}  (register 'mie': Machine Interrupt Enable) \n")
        elif register_num == 0x340:
            print(f"Tried to write CSR[0x{register_num:x}] = 0x{value:x}  (register 'mscratch': Scratch register) \n")
            self.CSR_mscratch = value
        elif register_num == 0x344:
            print(f"Tried to write CSR[0x{register_num:x}] = 0x{value:x}  (register 'mip': Machine Interrupt Pending) \n")
        else:
            print(f"[ERROR] Tried to write unknown CSR register -> CSR[0x{register_num:x}] = 0x{value:x} \n")
            exit()
        pass
