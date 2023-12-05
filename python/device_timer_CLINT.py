
# The module I'm emulating is actually called Core Local Interrupt (CLINT), but since I'll only use it for timer,
# I've decided not to give the module ambiguous name device_CLINT.py but also name it after the timer functionality

# The CLINT has 3 registers:
#   mtime - counts time (one tick is one microsecond in our case)
#   mtimeCmp - OS can set the timer value at/after which interrupt is triggered
#   msip - generates machine mode software interrupts when set
#
#   More info: https://chromitem-soc.readthedocs.io/en/latest/clint.html#register-map


class Device_Timer_CLINT:

    def __init__(self, logger, registers):
        self.logger = logger
        self.registers = registers
        self.timer_compare_value = 0
        self.MSIP_bit = 0
        pass

    def get_mtime(self):
        return self.registers.executed_instruction_counter

    def update(self):
        if self.timer_compare_value != 0 and self.get_mtime() > self.timer_compare_value:
            # self.logger.register_device_usage(f"[CLINT/TIMER] mTime ({self.get_mtime()}) bigger than mTimeCmp ({self.timer_compare_value}) !!!")

            self.registers.signal_timer_interrupt()
            pass
        pass

    def read_register(self, address):
        # self.logger.register_device_usage(f"[CLINT/TIMER] Read at {address:08x}")

        timer_val = self.get_mtime()

        # TODO: it would be easier to just have functions read/write 32 bit and than per byte access just wraps these functions
        if address == 0xBFF8:  # mtime register
            self.logger.register_device_usage(f"[CLINT/TIMER] Read at {address:08x}: {timer_val}")
            return timer_val & 0xFF
        elif address == 0xBFF9:
            return (timer_val >> 8) & 0xFF
        elif address == 0xBFFA:
            return (timer_val >> 16) & 0xFF
        elif address == 0xBFFB:
            return (timer_val >> 24) & 0xFF
        elif address == 0xBFFC:
            self.logger.register_device_usage(f"[CLINT/TIMER] Read at {address:08x}: {timer_val}")
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
        # self.logger.register_device_usage(f"[CLINT/TIMER] Write at {address:08x}: {value:08x}")

        if address == 0:  # MSIP Register
            bit_value = value & 0b00000001
            self.MSIP_bit = bit_value
            self.logger.register_device_usage(f"[CLINT/TIMER] Write at {address:08x}: {value:08x}")
        elif 1 <= address <= 7:
            # Only 1 bit of 32-bit MSIP Register is implemented. All other bits are hardwired to zero
            pass
        elif address == 0x4000:  # MtimeCmp Register
            self.timer_compare_value &= 0xFFFFFFFFFFFFFF00
            self.timer_compare_value |= value
        elif address == 0x4001:
            self.timer_compare_value &= 0xFFFFFFFFFFFF00FF
            self.timer_compare_value |= value << 8
        elif address == 0x4002:
            self.timer_compare_value &= 0xFFFFFFFFFF00FFFF
            self.timer_compare_value |= value << 16
        elif address == 0x4003:
            self.timer_compare_value &= 0xFFFFFFFF00FFFFFF
            self.timer_compare_value |= value << 24
        elif address == 0x4004:
            self.timer_compare_value &= 0xFFFFFF00FFFFFFFF
            self.timer_compare_value |= value << 32
        elif address == 0x4005:
            self.timer_compare_value &= 0xFFFF00FFFFFFFFFF
            self.timer_compare_value |= value << 40
        elif address == 0x4006:
            self.timer_compare_value &= 0xFF00FFFFFFFFFFFF
            self.timer_compare_value |= value << 48
        elif address == 0x4007:
            self.timer_compare_value &= 0x00FFFFFFFFFFFFFF
            self.timer_compare_value |= value << 56
            self.logger.register_device_usage(f"[CLINT/TIMER] Write at {address:08x}: {self.timer_compare_value}")
        else:
            print(f"[ERROR] CLINT/TIMER: Unknown/unimplemented register write attempt ({address:08x})")
            quit()
        pass
