# Wikipedia
#   https://en.wikipedia.org/wiki/8250_UART
#   https://en.wikipedia.org/wiki/16550_UART

# Registers
#   https://www.lammertbies.nl/comm/info/serial-uart

class Device_UART_8250:

    def __init__(self, logger):
        self.logger = logger
        pass

    def read_register(self, address):
        self.logger.register_device_usage(f"[UART] Read at {address}")
        return 0

    def write_register(self, address, value):
        self.logger.register_device_usage(f"[UART] Write at {address}: {value:08x}")
        pass
