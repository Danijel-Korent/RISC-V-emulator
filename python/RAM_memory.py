from config import *


class RAM_memory:

    def __init__(self, LINUX_IMAGE_PATH, DEVICE_TREE_PATH, RAM_size):

        self.RAM = bytearray()

        # Load the content of Linux image file into a bytearray
        with open(LINUX_IMAGE_PATH, 'rb') as file:
            linux_image_binary = bytearray(file.read())

        with open(DEVICE_TREE_PATH, 'rb') as file:
            device_tree_binary = bytearray(file.read())

        device_tree_address = RAM_SIZE - len(device_tree_binary) - 192  # 192 is implementation detail of the C emulator
        print(f"Calculated DTB address: {device_tree_address:08x}")

        # Beginning of RAM is filled with Linux
        self.RAM.extend(linux_image_binary)

        # The rest of RAM is just RAM_size (minus sizeof linux_image) of empty space
        self.RAM.extend(bytearray(RAM_size - len(linux_image_binary)))

        # Copy content of the device tree file into the RAM at specified address
        # TODO: Make this more readable
        self.RAM[device_tree_address:device_tree_address + len(device_tree_binary)] = device_tree_binary

        self.device_tree_address = device_tree_address

    def get_device_tree_RAM_address(self):
        return self.device_tree_address


if __name__ == '__main__':
    print(f"\nExecuting:\n\t{__file__} \n")
    print("Hopefully here we will have tests for functions in this file")
