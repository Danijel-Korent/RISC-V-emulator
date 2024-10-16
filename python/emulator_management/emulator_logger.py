from config import LOGGER_PRINT_DEVICE_ACTIVITY, LOGGER_PRINT_CSR_REGISTER_ACTIVITY, EXIT_EMULATOR_AT_INSTRUCTION_NO, \
    BREAKPOINT_AT_INSTRUCTION_NO, ReportType, LINKER_MAP_FILE_PATH


class Emulator_logger:

    def __init__(self, start_traceout_at_instruction_no=0, report_type=ReportType.SHORT_REPORT):
        self.instruction_counter = 0
        self.start_traceout_at_instruction_no = start_traceout_at_instruction_no
        self.last_report_at_instruction_no = 0
        self.report_type = report_type

        # Map file parsing
        self.symbols = []
        self.last_instruction_address = None

        # TODO: Handle "no file" exception
        with open(LINKER_MAP_FILE_PATH, 'r') as file:
            file_content = file.read()
            self.symbols = parse_linker_map_file(file_content)
        pass

    def register_one_CPU_step(self, instruction_value, registers, CSR_registers, memory, trap_and_interrupt_handler):
        self.instruction_counter += 1

        if self.instruction_counter >= self.start_traceout_at_instruction_no:
            self.last_instruction_address = registers.instruction_pointer

            if self.report_type == ReportType.SHORT_REPORT:
                print(f"({self.instruction_counter})  PC: {registers.instruction_pointer:08x} [{instruction_value:08x}]", end="")
                pass
            elif self.report_type == ReportType.LONG_REPORT:
                # Print informational data
                registers.print_register_values()
                print("\n===============================")
                print(f"Instruction no.:     {self.instruction_counter}")
                print("===============================")
                print(f"Instruction pointer: 0x{registers.instruction_pointer:08x}")
                print(f"Instruction value:   0x{instruction_value:08x} \n")
            elif self.report_type == ReportType.C_EMU_REPORT:
                print(f"Timer:{memory.get_4_bytes__little_endian(0x1100bff8):08x} PC: {registers.instruction_pointer:08x}"
                      f" [0x{instruction_value:08x}] Z:{registers.x[0]:08x} ra:{registers.x[1]:08x} sp:{registers.x[2]:08x}"
                      f" gp:{registers.x[3]:08x} tp:{registers.x[4]:08x} t0:{registers.x[5]:08x} t1:{registers.x[6]:08x}"
                      f" t2:{registers.x[7]:08x} s0:{registers.x[8]:08x} s1:{registers.x[9]:08x} a0:{registers.x[10]:08x}"
                      f" a1:{registers.x[11]:08x} a2:{registers.x[12]:08x} a3:{registers.x[13]:08x} a4:{registers.x[14]:08x}"
                      f" a5:{registers.x[15]:08x} a6:{registers.x[16]:08x} a7:{registers.x[17]:08x} s2:{registers.x[18]:08x}"
                      f" s3:{registers.x[19]:08x} s4:{registers.x[20]:08x} s5:{registers.x[21]:08x} s6:{registers.x[22]:08x}"
                      f" s7:{registers.x[23]:08x} s8:{registers.x[24]:08x} s9:{registers.x[25]:08x} s10:{registers.x[26]:08x}"
                      f" s11:{registers.x[27]:08x} t3:{registers.x[28]:08x} t4:{registers.x[29]:08x} t5:{registers.x[30]:08x}"
                      f" t6:{registers.x[31]:08x} mscratch:{CSR_registers.CSR_mscratch:08x}"
                      f" mstatus:{trap_and_interrupt_handler.get_register_mstatus():08x}"
                      f" privilege:{trap_and_interrupt_handler.CPU_privilege_mode}")
            else:
                pass
        else:
            if self.report_type != ReportType.C_EMU_REPORT:
                if self.instruction_counter - self.last_report_at_instruction_no >= 250000:
                    self.last_report_at_instruction_no = self.instruction_counter
                    # This could in some cases return symbol that is not a function, but I'll deal with that later
                    current_function = get_symbol_name(registers.instruction_pointer, self.symbols)
                    print(f"[EMULATOR] Executed {self.instruction_counter} instructions / CPU executing: {current_function}")
                    pass
        pass

    # TODO: Currently ordinary string is passed, should be replaced with something structured
    def register_executed_instruction(self, message):
        if self.instruction_counter >= self.start_traceout_at_instruction_no :
            if self.report_type == ReportType.SHORT_REPORT:
                current_function = get_symbol_name(self.last_instruction_address, self.symbols)
                print(f"   -> {message}   \t\t  [{current_function}]")
            elif self.report_type == ReportType.LONG_REPORT:
                print(f"Executed instruction -> {message} \n")
            else:
                pass

        if self.instruction_counter == EXIT_EMULATOR_AT_INSTRUCTION_NO:
            print('[EMULATOR] Exited by emulator')
            quit()
            # breakpoint()
            pass

        if self.instruction_counter - 1 == BREAKPOINT_AT_INSTRUCTION_NO:
            print('[EMULATOR] Breakpoint by emulator')
            breakpoint()
            pass
        pass

    def register_device_usage(self, message):
        if LOGGER_PRINT_DEVICE_ACTIVITY:
            print(f"[{self.instruction_counter}] {message}")
        pass

    def register_CSR_register_usage(self, message):
        if LOGGER_PRINT_CSR_REGISTER_ACTIVITY:
            print(f"[{self.instruction_counter}] {message}")


# Parse a ".map" file generated by linker and return a list of tuples (address, symbol_name)
def parse_linker_map_file(file_content):
    symbols = []
    for line in file_content.splitlines():
        parts = line.split()
        if len(parts) == 3:
            address, _, symbol = parts
            symbols.append((int(address, 16), symbol))
    # Sorting the symbols by address
    symbols.sort(key=lambda x: x[0])
    return symbols


# Find a symbol name for a given address and symbol list
# NOTE: The function doesn't cover corner cases and may return incorrect symbol on edge cases
def get_symbol_name(address, symbols):
    closest_symbol = 'Error parsing symbol'
    for symbol_address, symbol_name in symbols:
        if symbol_address <= address:
            closest_symbol = symbol_name
        else:
            break

    if closest_symbol == '_end':
        closest_symbol = 'Address outside of the kernel'
    else:
        closest_symbol += "()"

    return closest_symbol
