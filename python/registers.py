from config import START_ADDRESS_OF_RAM, TTY_OUTPUT_ENABLED


# TODO: Rename "register.py" to "CPU_registers.py".
# TODO: Move CSR stuff into "CSR_registers.py" if it grows to big after fully implementing CSR registers
class Registers:
    def __init__(self, logger):
        # All CPUs have one register that holds the address of the next instruction to execute
        # Here we also set the initial instruction address. Normal system would have ROM/flash memory (with initial
        # hardcoded bootloader) mapped into this address. We mapped at this address (a small chunk of) Linux kernel
        self.instruction_pointer = START_ADDRESS_OF_RAM

        self.logger = logger

        # An array of registers
        # RISC-V has 32 integer registers
        # https://en.wikipedia.org/wiki/RISC-V#Register_sets
        self.integer_regs = [
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0, 0, 0, 0,
                                 ]

        # CSR registers
        self.CSR_mscratch = 0
        self.CSR_mtvec = 0
        self.CSR_mstatus = 0

        # Register "Machine Interrupt Pending"
        self.CSR_mip = 0

        # Register "Machine Interrupt Enable"
        self.CSR_mie = 0

        # Register "Machine exception PC / Instruction pointer"
        self.CSR_mepc = 0

        # Register "Machine trap cause"
        self.CSR_mcause = 0

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

        # Print CSR registers
        print(f"CSR_mscratch: {self.CSR_mscratch:08x}")
        print(f"CSR_mtvec: {self.CSR_mtvec:08x}")

    def read_from_CSR_register(self, register_num):
        ret_val = 0

        if register_num == 0x139:
            # This name variables should be a table/dict from which we fetch the string
            register_short_name = "hvc0"
            register_long_name = "Xen hypervisor console"
        elif register_num == 0x300:
            register_short_name = "mstatus"
            register_long_name = "Machine status register"
            ret_val = self.CSR_mstatus
        elif register_num == 0x304:
            register_short_name = "mie"
            register_long_name = "Machine Interrupt Enable"
            ret_val = self.CSR_mie
        elif register_num == 0x305:
            register_short_name = "mtvec"
            register_long_name = "Machine trap-handler base address"
            ret_val = self.CSR_mtvec
        elif register_num == 0x340:
            register_short_name = "mscratch"
            register_long_name = "Scratch register"
            ret_val = self.CSR_mscratch
        elif register_num == 0x341:
            register_short_name = "mepc"
            register_long_name = "Machine exception PC / Instruction pointer"
            ret_val = self.CSR_mepc
        elif register_num == 0x342:
            register_short_name = "mcause"
            register_long_name = "Machine trap cause"
            ret_val = self.CSR_mcause
        elif register_num == 0x343:
            register_short_name = "mtval"
            register_long_name = "Machine bad address or instruction"
            ret_val = 0  # Unimplemented at the moment
        elif register_num == 0x344:
            register_short_name = "mip"
            register_long_name = "Machine Interrupt Pending"
            ret_val = self.CSR_mip
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

        message = f"Read  CSR[0x{register_num:x}], old value = {ret_val:08x} (register '{register_short_name}': {register_long_name})"
        self.logger.register_CSR_register_usage(message)
        return ret_val

    def write_to_CSR_register(self, register_num, new_value):
        if register_num == 0x139:
            # This is Xen hypervisor console
            # Because device tree has set "console=hvc0" in Kernel bootargs/cmdargs, the kernel switches
            # from UART to Xen console
            register_short_name = "hvc0"
            register_long_name = "Xen hypervisor console"
            if TTY_OUTPUT_ENABLED:
                char = chr(new_value)  # Convert value to ASCII character
                print(char, end='')
        elif register_num == 0x300:
            register_short_name = "mstatus"
            register_long_name = "Machine status register"
            self.CSR_mstatus = new_value
        elif register_num == 0x304:
            register_short_name = "mie"
            register_long_name = "Machine Interrupt Enable"
            self.CSR_mie = new_value
        elif register_num == 0x305:
            register_short_name = "mtvec"
            register_long_name = "Machine trap-handler base address"
            self.CSR_mtvec = new_value
        elif register_num == 0x340:
            register_short_name = "mscratch"
            register_long_name = "Scratch register"
            self.CSR_mscratch = new_value
        elif register_num == 0x341:
            register_short_name = "mepc"
            register_long_name = "Machine exception PC / Instruction pointer"
            self.CSR_mepc = new_value
        elif register_num == 0x342:
            register_short_name = "mcause"
            register_long_name = "Machine trap cause"
            self.CSR_mcause = new_value
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
        elif register_num == 0xF14:
            register_short_name = "mhartid"
            register_long_name = "Hardware thread ID"
        else:
            print(f"[ERROR] Tried to write unknown CSR register -> CSR[0x{register_num:x}] = 0x{new_value:x} \n")
            exit()

        message = f"Write CSR[0x{register_num:x}], new value = {new_value:08x} (register '{register_short_name}': {register_long_name})\n"
        self.logger.register_CSR_register_usage(message)
        pass

    # TODO: When moving this out of Class Registers, add functions get_MIP(), get_MIE() and similar
    def signal_timer_interrupt(self):
        # Machine Timer Interupt bit
        MTIP_bit_position = 7

        # Set pending interrupt bit for timer
        self.CSR_mip = (1 << MTIP_bit_position)
        #print(f"({self.executed_instruction_counter}) Called signal_timer_interrupt: CSR_mip = {self.CSR_mip:x}, CSR_mie = {self.CSR_mie:x}, CSR_mstatus = {self.CSR_mstatus:x}")
        pass

    def interrupt_controller_update(self):

        enabled_pending_interrupts = self.CSR_mip & self.CSR_mie

        # Replace "self.CSR_mstatus & 8 == 8" with are_interrupts_enabled() from Class interrupt_controller
        if enabled_pending_interrupts != 0 and self.CSR_mstatus & 8 == 8:

            #print(f"({self.executed_instruction_counter}) IRQ triggered: CSR_mip = {self.CSR_mip:x}, CSR_mie = {self.CSR_mie:x}, CSR_mstatus = {self.CSR_mstatus:x}")
            #print(f"({self.executed_instruction_counter}) IRQ triggered: enabled_pending_interrupts = {enabled_pending_interrupts:x}")

            # Set MIE to zero
            # TODO: Replace this with setting mstatus.mie to zero
            self.write_to_CSR_register(0x304, 0)

            # Save address of next instruction to CSR register "mepc"
            # TODO: Replace hardcoded value with a name
            self.write_to_CSR_register(0x341, self.instruction_pointer + 4)

            # Write the cause of the trap into the register "mcause"
            self.write_to_CSR_register(0x342, 0x80000000 + self.CSR_mip)

            # Jump to address specified in register "Machine Trap Vector"
            self.instruction_pointer = self.CSR_mtvec
            #print(f"({self.executed_instruction_counter}) IRQ triggered: Setting PC to trap vector")
        pass
