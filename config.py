from enum import Enum
from platform import system

class ReportType(Enum):
    NONE = 0
    SHORT_REPORT = 1
    LONG_REPORT = 2
    ONELINE_LONG_REPORT = 3
    ONLY_PROGRESS_REPORT = 4


# File paths
LINUX_IMAGE_PATH = 'Linux_kernel_image/Linux_image_6_1_14_RV32IMA_NoMMU'
DEVICE_TREE_PATH = 'Linux_kernel_image/device_tree_binary.dtb'
LINKER_MAP_FILE_PATH = 'Linux_kernel_image/debug_info/System.map'


# VM/Emulator address space
RAM_SIZE = 64*1024*1024
START_ADDRESS_OF_RAM  = 0x80000000
START_ADDRESS_OF_UART = 0x10000000
START_ADDRESS_OF_TIMER_CLINT = 0x11000000


# Options for easier debugging
TTY_OUTPUT_ENABLED = True
LOGGER_PRINT_DEVICE_ACTIVITY = False
LOGGER_PRINT_CSR_REGISTER_ACTIVITY = False

TEST_UART_INPUT = ""
LOGGER_REPORT_TYPE = ReportType.NONE
START_TRACEOUT_AT_INSTRUCTION_NO = None
STOP_TRACEOUT_AT_INSTRUCTION_NO = None
EXIT_EMULATOR_AT_INSTRUCTION_NO  = None
BREAKPOINT_AT_INSTRUCTION_NO = None


# Default settings for Windows and Linux
if system() == 'Windows' or system() == "Linux":
    TEST_UART_INPUT = ""
    START_TRACEOUT_AT_INSTRUCTION_NO = 0
    STOP_TRACEOUT_AT_INSTRUCTION_NO = 61000001
    LOGGER_REPORT_TYPE = ReportType.ONLY_PROGRESS_REPORT
else:
    TEST_UART_INPUT = "ls -lah / \r\n"
    START_TRACEOUT_AT_INSTRUCTION_NO = 0
    EXIT_EMULATOR_AT_INSTRUCTION_NO = 67750000
    LOGGER_REPORT_TYPE = ReportType.ONLY_PROGRESS_REPORT


# Easy on/off switch for debugging (outputs first 15 instructions by default)
if 0:
    START_TRACEOUT_AT_INSTRUCTION_NO = 0
    STOP_TRACEOUT_AT_INSTRUCTION_NO = 15
    EXIT_EMULATOR_AT_INSTRUCTION_NO = None
    LOGGER_REPORT_TYPE = ReportType.SHORT_REPORT
    TTY_OUTPUT_ENABLED = True
