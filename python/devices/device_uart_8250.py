# Wikipedia
#   https://en.wikipedia.org/wiki/8250_UART
#   https://en.wikipedia.org/wiki/16550_UART
from config import TTY_OUTPUT_ENABLED


# Registers
#   https://www.lammertbies.nl/comm/info/serial-uart

class Device_UART_8250:

    def __init__(self, logger):
        self.logger = logger
        self.test_UART_input = "uname -a\13"
        pass

    def read_register(self, address):
        self.logger.register_device_usage(f"[UART] Read at {address:08x}")

        # TODO:
        #   - add "if address == 0" for reading the RBR receiver buffer
        #   - As a test, just add hardcoded "uname -a" triggered at specific instruction count
        #     - this is also a nice excuse to play with py generators
        #     - don't forget to tell Linux to read the RX (return 0x61 from reg 5)

        # Line Status Register (LSR)
        if address == 0:
            if len(self.test_UART_input) > 0 and self.logger.instruction_counter > 62740000:
                char = self.test_UART_input[0]
                self.test_UART_input = self.test_UART_input[1:] # remove first char
                return char
            else:
                return 0
        if address == 5:
            TRANSMIT_BUFFER_IS_EMPTY = 0b00100000
            TRANSMIT_LINE_IS_IDLE = 0b01000000
            DATA_AVAILABLE = 0b01000001

            retVal = TRANSMIT_BUFFER_IS_EMPTY + TRANSMIT_LINE_IS_IDLE

            if len(self.test_UART_input) > 0 and self.logger.instruction_counter > 62740000:
                retVal += DATA_AVAILABLE

            # If software asks about status, we always tell that TX line is ready for transmission
            return retVal

        return 0

    def write_register(self, address, value):
        self.logger.register_device_usage(f"[UART] Write at {address:08x}: {value:08x}")

        # transmitter buffer register - THR (if DLAB=0 which we don't check)
        # Everything that is put into this register should be outputted by UART as data
        if address == 0 and TTY_OUTPUT_ENABLED:
            char = chr(value)  # Convert value to ASCII character
            print(char, end='')
            pass

        pass
