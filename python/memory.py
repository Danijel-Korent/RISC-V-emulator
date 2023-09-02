

class Memory:
    def __init__(self, linux_image_path, RAM_size):

        # Load the content of Linux image file into a bytearray
        with open(linux_image_path, 'rb') as f:
            Linux_bytes = bytearray(f.read())

        self.RAM = bytearray()

        # Beginning of RAM is filled with Linux
        self.RAM.extend(Linux_bytes)

        # The rest of RAM is just RAM_size (minus sizeof linux_image) of empty space
        self.RAM.extend( bytearray(RAM_size - len(Linux_bytes)))

    # Returns a value stored at specified address
    def get_1_byte(self, address):
        if address >= 0x80000000:
            RAM_addr = address - 0x80000000
            return self.RAM[RAM_addr]

        return 0

    def write_1_byte(self, address, value):
        if address >= 0x80000000:
            RAM_addr = address - 0x80000000
            self.RAM[RAM_addr] = value
        else:
            print("[ERROR] RAM: trying to write to unimplemented address")
            quit()

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
