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

    def register_one_CPU_step(self, registers, instruction_value, memory):
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
                print(f"Timer:{memory.get_4_bytes__little_endian(0x1100bff8):08x} PC: {registers.instruction_pointer:08x} [0x{instruction_value:08x}] Z:{registers.integer_regs[0]:08x} ra:{registers.integer_regs[1]:08x} sp:{registers.integer_regs[2]:08x} gp:{registers.integer_regs[3]:08x} tp:{registers.integer_regs[4]:08x} t0:{registers.integer_regs[5]:08x} t1:{registers.integer_regs[6]:08x} t2:{registers.integer_regs[7]:08x} s0:{registers.integer_regs[8]:08x} s1:{registers.integer_regs[9]:08x} a0:{registers.integer_regs[10]:08x} a1:{registers.integer_regs[11]:08x} a2:{registers.integer_regs[12]:08x} a3:{registers.integer_regs[13]:08x} a4:{registers.integer_regs[14]:08x} a5:{registers.integer_regs[15]:08x} a6:{registers.integer_regs[16]:08x} a7:{registers.integer_regs[17]:08x} s2:{registers.integer_regs[18]:08x} s3:{registers.integer_regs[19]:08x} s4:{registers.integer_regs[20]:08x} s5:{registers.integer_regs[21]:08x} s6:{registers.integer_regs[22]:08x} s7:{registers.integer_regs[23]:08x} s8:{registers.integer_regs[24]:08x} s9:{registers.integer_regs[25]:08x} s10:{registers.integer_regs[26]:08x} s11:{registers.integer_regs[27]:08x} t3:{registers.integer_regs[28]:08x} t4:{registers.integer_regs[29]:08x} t5:{registers.integer_regs[30]:08x} t6:{registers.integer_regs[31]:08x}")
            else:
                pass
        else:
            if self.report_type != ReportType.C_EMU_REPORT:
                if self.instruction_counter - self.last_report_at_instruction_no >= 250000:
                    self.last_report_at_instruction_no = self.instruction_counter
                    current_function = get_symbol_name(registers.instruction_pointer, self.symbols)
                    print(f"({self.instruction_counter}) Executed 250,000 instructions [CPU currently executing: {current_function}]")
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
            print('[MANAGER] Exited by manager')
            quit()
            # breakpoint()
            pass

        if self.instruction_counter - 1 == BREAKPOINT_AT_INSTRUCTION_NO:
            print('[MANAGER] Breakpoint by manager')
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

    return closest_symbol
