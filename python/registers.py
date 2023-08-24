

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
        self.CSR_mtvec = 0

    def print_register_values(self):
        # just to shorten the variable name
        reg = self.integer_regs

        # Print all integer registers
        for i in range(8):
            offset = i*4
            for x in range(4):
                reg_no = offset + x
                print(f"x{reg_no:02}: {reg[reg_no]:08x}, ", end='')
            # just for new line
            print("")

        # Print CSR registers
        print(f"CSR_mscratch: {self.CSR_mscratch:08x}")
        print(f"CSR_mtvec: {self.CSR_mtvec:08x}")

    def read_from_CSR_register(self, register_num):
        ret_val = 0

        if register_num == 0x304:
            register_short_name = "mie"
            register_long_name = "Machine Interrupt Enable"
        elif register_num == 0x305:
            register_short_name = "mtvec"
            register_long_name = "Machine trap-handler base address"
            ret_val = self.CSR_mtvec
        elif register_num == 0x340:
            register_short_name = "mscratch"
            register_long_name = "Scratch register"
            ret_val = self.CSR_mscratch
        elif register_num == 0x344:
            register_short_name = "mip"
            register_long_name = "Machine Interrupt Pending"
        elif register_num == 0x3a0:
            register_short_name = "pmpcfg0"
            register_long_name = "Physical memory protection configuration"
        elif register_num == 0x3b0:
            register_short_name = "pmpaddr0"
            register_long_name = "Physical memory protection address register"
        elif register_num == 0xF14:
            register_short_name = "mhartid"
            register_long_name = "Hardware thread ID"
            ret_val = 0  # Number returned by original C emulator
        else:
            print(f"[ERROR] Tried to read unknown CSR register -> CSR[0x{register_num:x}]")
            exit()

        print(f"Read  CSR[0x{register_num:x}], old value = {ret_val:08x} (register '{register_short_name}': {register_long_name})")
        return ret_val

    def write_to_CSR_register(self, register_num, new_value):
        if register_num == 0x304:
            register_short_name = "mie"
            register_long_name = "Machine Interrupt Enable"
        elif register_num == 0x305:
            register_short_name = "mtvec"
            register_long_name = "Machine trap-handler base address"
            self.CSR_mtvec = new_value
        elif register_num == 0x340:
            register_short_name = "mscratch"
            register_long_name = "Scratch register"
            self.CSR_mscratch = new_value
        elif register_num == 0x344:
            register_short_name = "mip"
            register_long_name = "Machine Interrupt Pending"
        elif register_num == 0x3a0:
            register_short_name = "pmpcfg0"
            register_long_name = "Physical memory protection configuration"
        elif register_num == 0x3b0:
            register_short_name = "pmpaddr0"
            register_long_name = "Physical memory protection address register"
        elif register_num == 0xF14:
            register_short_name = "mhartid"
            register_long_name = "Hardware thread ID"
        else:
            print(f"[ERROR] Tried to write unknown CSR register -> CSR[0x{register_num:x}] = 0x{new_value:x} \n")
            exit()

        print(f"Write CSR[0x{register_num:x}], new value = {new_value:08x} (register '{register_short_name}': {register_long_name})\n")
        pass
