

class Emulator_logger:

    def __init__(self, start_traceout_at_instruction_no=0, short_report=False):
        self.instruction_counter = 0
        self.start_traceout_at_instruction_no = start_traceout_at_instruction_no
        self.last_report_at_instruction_no = 0
        self.short_report = short_report
        pass

    def register_one_CPU_step(self, registers, instruction_value):
        self.instruction_counter += 1

        if self.instruction_counter >= self.start_traceout_at_instruction_no :
            if self.short_report:
                print(f"({self.instruction_counter})  PC: {registers.instruction_pointer:08x} [{instruction_value:08x}]", end="")
                pass
            else:
                # Print informational data
                registers.print_register_values()
                print("\n===============================")
                print(f"Instruction no.:     {self.instruction_counter}")
                print("===============================")
                print(f"Instruction pointer: 0x{registers.instruction_pointer:08x}")
                print(f"Instruction value:   0x{instruction_value:08x} \n")
        else:
            if self.instruction_counter - self.last_report_at_instruction_no >= 50000:
                self.last_report_at_instruction_no = self.instruction_counter
                print(f"[{self.instruction_counter}] Executed 50,000 instructions")
        pass

    def register_executed_instruction(self, message):
        if self.instruction_counter >= self.start_traceout_at_instruction_no :
            if self.short_report:
                print(f"   -> {message}")
            else:
                print(f"Executed instruction -> {message} \n")

        if self.instruction_counter == 340940 + 0:
            print('[MANAGER] Exited by manager')
            quit()
            # breakpoint()
            pass
        pass

    def register_device_usage(self, message):
        print(f"[{self.instruction_counter}] {message}")
