
class Trap_And_Interrupt_Handler:

    def __init__(self, registers, logger):
        self.logger = logger  # TODO: Just make it singleton
        self.CPU_registers = registers
        self.interrupts_global_enable = False
        self.MPIE__Previous_Interrupt_Enable = False
        self.MPP__Previous_Priviledge_Mode = 0

        # CSR registers
        self.CSR_mtvec = 0
        #self.CSR_mstatus = 0

        # Register "Machine Interrupt Pending"
        self.CSR_mip = 0

        # Register "Machine Interrupt Enable"
        self.CSR_mie = 0

        # Register "Machine exception PC / Instruction pointer"
        self.CSR_mepc = 0

        # Register "Machine trap cause"
        self.CSR_mcause = 0
        pass

    # TODO: When moving this out of Class Registers, add functions get_MIP(), get_MIE() and similar
    def signal_timer_interrupt(self):
        # Machine Timer Interupt bit
        MTIP_bit_position = 7

        # Set pending interrupt bit for timer
        # TODO: The problem is, MIP should be read from the controller if we want to be precise
        self.CSR_mip = (1 << MTIP_bit_position)
        # print(f"({self.executed_instruction_counter}) Called signal_timer_interrupt: CSR_mip = {self.CSR_mip:x}, CSR_mie = {self.CSR_mie:x}, CSR_mstatus = {self.CSR_mstatus:x}")
        pass

    def clear_timer_interrupt(self):
        # Machine Timer Interupt bit
        MTIP_bit_position = 7

        # TODO: There are no other interrupts at the moment, so just clear all
        self.CSR_mip = 0


    def update(self):
        # Check if there are any pending interrupts (MIP), and if the pending interrupts are enabled (MIE)
        enabled_pending_interrupts = self.CSR_mip & self.CSR_mie

        # Replace "self.CSR_mstatus & 8 == 8" with are_interrupts_enabled() from Class interrupt_controller
        if enabled_pending_interrupts != 0 and self.get_interrupts_global_enable_state():
            self.enter_interrupt()
        pass

    def enter_interrupt(self):
        # print(f"({self.executed_instruction_counter}) IRQ triggered: CSR_mip = {self.CSR_mip:x}, CSR_mie = {self.CSR_mie:x}, CSR_mstatus = {self.CSR_mstatus:x}")
        # print(f"({self.executed_instruction_counter}) IRQ triggered: enabled_pending_interrupts = {enabled_pending_interrupts:x}")

        # Set MPIE to current MIE
        self.set_MPIE__Previous_Interrupt_Enable(self.get_interrupts_global_enable_state())

        # Set MPP (Machine Previous Priviledge) to current privilage mode
        # TODO: Misspelled "privilege" everywhere. To my defense, google says it's a quite common mistake
        self.set_MPP__Previous_Priviledge_Mode(self.get_CPU_priviledge_mode())

        # Set mstatus.MIE to zero
        # setting mstatus.mie to zero
        self.set_interrupts_global_enable_state(False)

        # Save address of next instruction to CSR register "mepc"
        # TODO: Move CSR names into enum
        # CSR_MEPC_REGNUM = 0x341
        # self.write_to_CSR_register(CSR_MEPC_REGNUM, self.instruction_pointer)
        self.CSR_mepc = self.CPU_registers.instruction_pointer  # TODO: Where to keep instruction pointer? Here, trap_handler or registers.py?

        # Write the cause of the trap into the register "mcause"
        # TODO: Make a enum for EXCCODEs
        mcause_val = 0x80000000 + 7  # 7 is the "exception code" (EXCCODE) for the "Machine timer interrupt"
        # self.write_to_CSR_register(0x342, mcause_val)
        self.CSR_mcause = mcause_val

        # Jump to address specified in register "Machine Trap Vector"
        self.CPU_registers.instruction_pointer = self.CSR_mtvec
        # print(f"({self.executed_instruction_counter}) IRQ triggered: Setting PC to trap vector")
        pass

    def return_from_interrupt(self):
        # Setting pc to mepc
        # TODO: Move CSR names into enum
        # CSR_MEPC_REGNUM = 0x341
        # self.instruction_pointer = self.read_from_CSR_register(CSR_MEPC_REGNUM)
        self.CPU_registers.instruction_pointer = self.CSR_mepc

        # restoring the interrupt state (mstatus.mie)
        self.set_interrupts_global_enable_state(self.MPIE__Previous_Interrupt_Enable)

        # restore machine privilege mode
        # Currently we are always machine mode (3), will implement that later

    def set_MPIE__Previous_Interrupt_Enable(self, new_value: bool):
        self.logger.register_CSR_register_usage(f"[CPU Control] Setting MPIE__Previous_Interrupt_Enable to {new_value}")
        self.MPIE__Previous_Interrupt_Enable = new_value


    def set_MPP__Previous_Priviledge_Mode(self, new_value: int):
        if new_value > 3: raise Exception("Trying to set priviledge mode above 3: There are only 0-3 privilage modes")

        self.logger.register_CSR_register_usage(f"  [CPU Control] Setting MPP__Previous_Priviledge_Mode to {new_value}")

        self.MPP__Previous_Priviledge_Mode = new_value


    def get_CPU_priviledge_mode(self):
        # TODO: Add enum for privilages
        # TODO: Replace 3 with enum

        # Currently we are always in a "machine" mode
        return 3


    # TODO: Rename to get_interrupts_globally_enabled ??
    def get_interrupts_global_enable_state(self) -> bool:
        return self.interrupts_global_enable


    def set_interrupts_global_enable_state(self, new_state: bool):
        self.interrupts_global_enable = new_state


    ### CSR registers implementation
    # TODO: This doesn't belong to trap_and_interrupt_handler.py
    def set_register_mstatus(self, new_value):
        # TODO: Duplicated
        mask_mstatus_MIE = 0x8
        mask_mstatus_MPIE = 0x80

        masked_value = new_value & (mask_mstatus_MIE + mask_mstatus_MPIE)

        # if masked_value != new_value:
        #    raise Exception("CSR mstatus: Trying to write to non-writable bit")

        # Get changed bits with XOR
        changed_bits = self.get_register_mstatus() ^ new_value

        if changed_bits:
            if changed_bits & mask_mstatus_MIE == mask_mstatus_MIE:
                new_MIE_value = new_value & mask_mstatus_MIE
                if new_MIE_value:
                    self.set_interrupts_global_enable_state(True)
                else:
                    self.set_interrupts_global_enable_state(False)

            # TODO: Move to a function to make it more readable and re-usable
            if changed_bits & mask_mstatus_MPIE == mask_mstatus_MPIE:
                new_MPIE_value = new_value & mask_mstatus_MPIE
                if new_MPIE_value:
                    self.MPIE__Previous_Interrupt_Enable = True
                else:
                    self.MPIE__Previous_Interrupt_Enable = False
        pass

    # TODO: This doesn't belong to trap_and_interrupt_handler.py
    def get_register_mstatus(self):
        mstatus_value = 0

        # TODO: Duplicated
        mask_mstatus_MIE = 0x8
        mask_mstatus_MPIE = 0x80

        if self.get_interrupts_global_enable_state() == True:
            mstatus_value |= mask_mstatus_MIE

        if self.MPIE__Previous_Interrupt_Enable == True:
            mstatus_value |= mask_mstatus_MPIE

        MPP = self.MPP__Previous_Priviledge_Mode << 11

        mstatus_value |= MPP

        return mstatus_value

    ########## TRAP AND INTERRUPT CODE ############

    def set_trap_handler_address(self, address):
        self.CSR_mtvec = address
        pass

    def get_trap_handler_address(self):
        return self.CSR_mtvec
