
# The module I'm emulating is actually called Core Local Interrupt (CLINT), but since I'll only use it for timer,
# I've decided not to give the module ambiguous name device_CLINT.py but also name it after the timer functionality

# The CLINT has 3 registers, out of which I suspect I will only use the "mtime":
#   https://chromitem-soc.readthedocs.io/en/latest/clint.html#register-map


class Device_Timer_CLINT:

    def __init__(self, logger, registers):
        self.logger = logger
        self.registers = registers
        pass

    def read_register(self, address):
        self.logger.register_device_usage(f"[CLINT/TIMER] Read at {address}")

        timer_val = self.registers.executed_instruction_counter + 1

        if address == 0xBFF8:
            return timer_val & 0xFF
        elif address == 0xBFF9:
            return (timer_val >> 8) & 0xFF
        elif address == 0xBFFA:
            return (timer_val >> 16) & 0xFF
        elif address == 0xBFFB:
            return (timer_val >> 24) & 0xFF
        elif address == 0xBFFC:
            return (timer_val >> 32) & 0xFF
        elif address == 0xBFFD:
            return (timer_val >> 40) & 0xFF
        elif address == 0xBFFE:
            return (timer_val >> 48) & 0xFF
        elif address == 0xBFFF:
            return (timer_val >> 56) & 0xFF
        else:
            print(f"[ERROR] CLINT/TIMER: Unknown/unimplemented register read attempt ({address:08x})")
            quit()
        return 0

    def write_register(self, address, value):
        self.logger.register_device_usage(f"[CLINT/TIMER] Write at {address}: {value:08x}")

        print(f"[ERROR] CLINT/TIMER: Unknown/unimplemented register write attempt ({address:08x})")

        quit()
        pass
