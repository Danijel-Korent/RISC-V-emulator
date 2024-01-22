from config import START_ADDRESS_OF_RAM, TTY_OUTPUT_ENABLED


# TODO: Rename "register.py" to "CPU_registers.py".
# TODO: Move CSR stuff into "CSR_registers.py" if it grows to big after fully implementing CSR registers
class Registers:
    def __init__(self, logger):
        self.logger = logger

        # All CPUs have one register that holds the address of the next instruction to execute
        # Here we also set the initial instruction address. Normal system would have ROM/flash memory (with initial
        # hardcoded bootloader) mapped into this address. We mapped at this address (a small chunk of) Linux kernel
        self.instruction_pointer = START_ADDRESS_OF_RAM

        # An array of registers
        # RISC-V has 32 integer registers
        # https://en.wikipedia.org/wiki/RISC-V#Register_sets
        self.integer_regs = [
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                 ]

        # Internal implementation details, not directly visible/exposed via CPU instructions
        self.atomic_load_reserved__address = 0

        # Just counts the number of instructions executed so far. We need this for implementing deterministic timer
        self.executed_instruction_counter = 0


    def print_register_values(self):
        # just to shorten the variable name
        reg = self.integer_regs

        register_ABI_name = ["000", "ra ", "sp ", "gp ", "tp ", "t00", "t01", "t02",
                             "fp ", "s01", "a00", "a01", "a02", "a03", "a04", "a05",
                             "a06", "a07", "s02", "s03", "s04", "s05", "s06", "s07",
                             "s08", "s09", "s10", "s11", "t03", "t04", "t05", "t06"]

        # Print all integer registers
        for i in range(8):
            offset = i*4
            for x in range(4):
                reg_no = offset + x
                print(f"x{reg_no:02},{register_ABI_name[reg_no]}: {reg[reg_no]:08x}   ", end='')
            # just for new line
            print("")

        # TODO: This will have to be moved to class CSR_Registers
        # Print CSR registers
        # print(f"CSR_mscratch: {self.CSR_mscratch:08x}")
        # print(f"CSR_mtvec: {self.CSR_mtvec:08x}")


class CSR_Registers:
    def __init__(self, trap_and_interrupt_handler, logger):
        self.trap_and_interrupt_handler = trap_and_interrupt_handler
        self.logger = logger

        # CSR registers
        self.CSR_mscratch = 0

    def read_from_register(self, register_num):
        ret_val = 0

        if register_num == 0x139:
            # This name variables should be a table/dict from which we fetch the string
            register_short_name = "hvc0"
            register_long_name = "Xen hypervisor console"
        elif register_num == 0x140:
            # TODO: This should probably be implemented as real register
            register_short_name = "sscratch"
            register_long_name = "Scratch register for supervisor trap handlers"
        elif register_num == 0x300:
            register_short_name = "mstatus"
            register_long_name = "Machine status register"
            ret_val = self.trap_and_interrupt_handler.get_register_mstatus()
        elif register_num == 0x304:
            register_short_name = "mie"
            register_long_name = "Machine Interrupt Enable"
            ret_val = self.trap_and_interrupt_handler.CSR_mie
        elif register_num == 0x305:
            register_short_name = "mtvec"
            register_long_name = "Machine trap-handler base address"
            ret_val = self.trap_and_interrupt_handler.get_trap_handler_address()
        elif register_num == 0x340:
            register_short_name = "mscratch"
            register_long_name = "Scratch register"
            ret_val = self.CSR_mscratch
        elif register_num == 0x341:
            register_short_name = "mepc"
            register_long_name = "Machine exception PC / Instruction pointer"
            ret_val = self.trap_and_interrupt_handler.CSR_mepc
        elif register_num == 0x342:
            register_short_name = "mcause"
            register_long_name = "Machine trap cause"
            ret_val = self.trap_and_interrupt_handler.CSR_mcause
        elif register_num == 0x343:
            register_short_name = "mtval"
            register_long_name = "Machine bad address or instruction"
            ret_val = 0  # Unimplemented at the moment
        elif register_num == 0x344:
            register_short_name = "mip"
            register_long_name = "Machine Interrupt Pending"
            ret_val = self.trap_and_interrupt_handler.CSR_mip
        elif register_num == 0x3a0:
            register_short_name = "pmpcfg0"
            register_long_name = "Physical memory protection configuration"
        elif register_num == 0x3b0:
            register_short_name = "pmpaddr0"
            register_long_name = "Physical memory protection address register"
        elif register_num == 0xF11:
            register_short_name = "mvendorid"
            register_long_name = "Machine Vendor ID"
            ret_val = 0xff0ff0ff  # Number returned by original C emulator
        elif register_num == 0xF11:
            register_short_name = "mvendorid"
            register_long_name = "Machine Vendor ID"
        elif register_num == 0xF12:
            register_short_name = "marchid"
            register_long_name = "Machine Architecture ID"
        elif register_num == 0xF13:
            register_short_name = "mimpid"
            register_long_name = "Machine Implementation ID"
        elif register_num == 0xF14:
            register_short_name = "mhartid"
            register_long_name = "Hardware thread ID"
            ret_val = 0  # First and only CPU core
        else:
            print(f"[ERROR] Tried to read unknown CSR register -> CSR[0x{register_num:x}]")
            exit()

        message = f"Read  CSR[0x{register_num:x}], old value = {ret_val:08x} (register '{register_short_name}': {register_long_name})"
        self.logger.register_CSR_register_usage(message)
        return ret_val

    def write_to_register(self, register_num, new_value):
        if register_num == 0x139:
            # This is Xen hypervisor console
            # Because device tree has set "console=hvc0" in Kernel bootargs/cmdargs, the kernel switches
            # from UART to Xen console
            register_short_name = "hvc0"
            register_long_name = "Xen hypervisor console"
            if TTY_OUTPUT_ENABLED:
                char = chr(new_value)  # Convert value to ASCII character
                print(char, end='')
        elif register_num == 0x140:
            register_short_name = "sscratch"
            register_long_name = "Scratch register for supervisor trap handlers"
        elif register_num == 0x300:
            register_short_name = "mstatus"
            register_long_name = "Machine status register"
            self.trap_and_interrupt_handler.set_register_mstatus(new_value)
        elif register_num == 0x304:
            register_short_name = "mie"
            register_long_name = "Machine Interrupt Enable"
            self.trap_and_interrupt_handler.CSR_mie = new_value
        elif register_num == 0x305:
            register_short_name = "mtvec"
            register_long_name = "Machine trap-handler base address"
            self.trap_and_interrupt_handler.set_trap_handler_address(new_value)
        elif register_num == 0x340:
            register_short_name = "mscratch"
            register_long_name = "Scratch register"
            self.CSR_mscratch = new_value
        elif register_num == 0x341:
            register_short_name = "mepc"
            register_long_name = "Machine exception PC / Instruction pointer"
            self.trap_and_interrupt_handler.CSR_mepc = new_value
        elif register_num == 0x342:
            register_short_name = "mcause"
            register_long_name = "Machine trap cause"
            self.trap_and_interrupt_handler.CSR_mcause = new_value # TODO: This probably should not be settable
        elif register_num == 0x343:
            register_short_name = "mtval"
            register_long_name = "Machine bad address or instruction"
            # Unimplemented at the moment
        elif register_num == 0x344:
            register_short_name = "mip"
            register_long_name = "Machine Interrupt Pending"
            self.CSR_mip = new_value
        elif register_num == 0x3a0:
            register_short_name = "pmpcfg0"
            register_long_name = "Physical memory protection configuration"
        elif register_num == 0x3b0:
            register_short_name = "pmpaddr0"
            register_long_name = "Physical memory protection address register"
        elif register_num == 0xF11:
            register_short_name = "mvendorid"
            register_long_name = "Machine Vendor ID"
        elif register_num == 0xF12:
            register_short_name = "marchid"
            register_long_name = "Machine Architecture ID"
        elif register_num == 0xF13:
            register_short_name = "mimpid"
            register_long_name = "Machine Implementation ID"
        elif register_num == 0xF14:
            register_short_name = "mhartid"
            register_long_name = "Hardware thread ID"
        else:
            print(f"[ERROR] Tried to write unknown CSR register -> CSR[0x{register_num:x}] = 0x{new_value:x} \n")
            exit()

        message = f"Write CSR[0x{register_num:x}], new value = {new_value:08x} (register '{register_short_name}': {register_long_name})\n"
        self.logger.register_CSR_register_usage(message)
        pass
