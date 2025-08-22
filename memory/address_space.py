from config import *


class Address_Space:

    def __init__(self, RAM_memory, device_UART, device_timer_CLINT):

        self.RAM_memory = RAM_memory
        self.device_UART = device_UART
        self.device_timer_CLINT = device_timer_CLINT

        print(f" [EMULATOR] CPU address space: ")
        print(f" [EMULATOR]     {START_ADDRESS_OF_UART:08X}-{START_ADDRESS_OF_UART+device_UART.get_mmio_size():08X} : UART")
        print(f" [EMULATOR]     {START_ADDRESS_OF_TIMER_CLINT:08X}-{START_ADDRESS_OF_TIMER_CLINT+device_timer_CLINT.get_mmio_size():08X} : CLINT")
        print(f" [EMULATOR]     {START_ADDRESS_OF_RAM:08X}-{START_ADDRESS_OF_RAM+RAM_SIZE:08X} : RAM")


    # Returns a value stored at specified address
    def get_1_byte(self, address):

        # TODO: We just repeat the same code for every device. It would be wise to just make a list of devices with
        #       common interface and just iterate over the list. Read/write functions are already common, just needs
        #       variables for starting address and size of memory map
        if START_ADDRESS_OF_RAM <= address <= START_ADDRESS_OF_RAM + RAM_SIZE:
            RAM_addr = address - START_ADDRESS_OF_RAM
            return self.RAM_memory.RAM[RAM_addr]

        elif START_ADDRESS_OF_UART <= address <= START_ADDRESS_OF_UART + self.device_UART.get_mmio_size():
            reg_address = address - START_ADDRESS_OF_UART
            return self.device_UART.read_register(reg_address)

        elif START_ADDRESS_OF_TIMER_CLINT <= address <= START_ADDRESS_OF_TIMER_CLINT + self.device_timer_CLINT.get_mmio_size():
            reg_address = address - START_ADDRESS_OF_TIMER_CLINT
            return self.device_timer_CLINT.read_register(reg_address)

        else:
            print(f"[ERROR] Address space: trying to read to unimplemented address: 0x{address:08x}")
            raise Exception("Address space: trying to read to unimplemented address")

    def write_1_byte(self, address, value):
        if START_ADDRESS_OF_RAM <= address <= START_ADDRESS_OF_RAM + RAM_SIZE:
            RAM_addr = address - START_ADDRESS_OF_RAM
            self.RAM_memory.RAM[RAM_addr] = value

        elif START_ADDRESS_OF_UART <= address <= START_ADDRESS_OF_UART + 8:
            reg_address = address - START_ADDRESS_OF_UART
            return self.device_UART.write_register(reg_address, value)

        elif START_ADDRESS_OF_TIMER_CLINT <= address <= START_ADDRESS_OF_TIMER_CLINT + 0xBFFF:
            reg_address = address - START_ADDRESS_OF_TIMER_CLINT
            return self.device_timer_CLINT.write_register(reg_address, value)

        else:
            print(f"[ERROR] Address space: trying to write to unimplemented address: 0x{address:08x}")
            raise Exception("Address space: trying to write to unimplemented address")

    # Read 32bits/4bytes starting from specified address
    # RISC-V starts in little endian mode, therefor we need to read data as little endian order
    def get_4_bytes__little_endian(self, address):
        # When you read byte-by-byte you will get the same value in both little endian CPU (LE) and big endian CPU (BE)
        # But if you read more than a byte into a register, LE and BE CPUs will put individual bytes into different
        # places in the register. It is similar to how some cultures read from left-to-right and some from right-to-left
        # If we imagine that single byte contains only single digit then following 4-bytes in memory [1,2,3,4] are read
        # by one CPU as number "1234" while a CPU with opposite endianness will read the same 4 bytes as a number "4321"
        #
        # Same is for writing a register into memory. In case of 32-bit (4 byte) register, LE and BE CPUs will
        # put individual bytes of register into different places in memory.
        # https://en.wikipedia.org/wiki/Endianness#Overview
        byte0 = self.get_1_byte(address)
        byte1 = self.get_1_byte(address + 1)
        byte2 = self.get_1_byte(address + 2)
        byte3 = self.get_1_byte(address + 3)

        value = (byte3 << 24) + (byte2 << 16) + (byte1 << 8) + byte0

        return value

    def get_2_bytes__little_endian(self, address):
        byte0 = self.get_1_byte(address)
        byte1 = self.get_1_byte(address + 1)

        value = (byte1 << 8) + byte0

        return value

    def write_4_bytes__little_endian(self, address, value):
        # Break the 32-bit value into individual bytes
        byte0 = value & 0xFF
        byte1 = (value >> 8) & 0xFF
        byte2 = (value >> 16) & 0xFF
        byte3 = (value >> 24) & 0xFF

        # Write each byte to memory in little-endian order
        self.write_1_byte(address, byte0)
        self.write_1_byte(address + 1, byte1)
        self.write_1_byte(address + 2, byte2)
        self.write_1_byte(address + 3, byte3)
        pass

    def write_2_bytes__little_endian(self, address, value):
        # Break the 16-bit value into individual bytes
        byte0 = value & 0xFF
        byte1 = (value >> 8) & 0xFF

        # Write each byte into memory in little-endian order
        self.write_1_byte(address, byte0)
        self.write_1_byte(address + 1, byte1)
        pass


if __name__ == '__main__':
    print(f"\nExecuting:\n\t{__file__} \n")
    print("Hopefully here we will have tests for functions in this file")
