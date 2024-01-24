from enum import Enum

class ReportType(Enum):
    SHORT_REPORT = 1
    LONG_REPORT = 2
    C_EMU_REPORT = 3


# System configuration
LINUX_IMAGE_PATH = 'Linux_kernel_image/Linux_image_6_1_14_RV32IMA_NoMMU'
DEVICE_TREE_PATH = 'Linux_kernel_image/device_tree_binary.dtb'
LINKER_MAP_FILE_PATH = 'Linux_kernel_image/debug_info/System.map'

RAM_SIZE = 64*1024*1024
START_ADDRESS_OF_RAM  = 0x80000000
START_ADDRESS_OF_UART = 0x10000000
START_ADDRESS_OF_TIMER_CLINT = 0x11000000

# Debug options configuration
START_TRACEOUT_AT_INSTRUCTION_NO = 39691178
EXIT_EMULATOR_AT_INSTRUCTION_NO  = 39691178 + 10
BREAKPOINT_AT_INSTRUCTION_NO = None

LOGGER_PRINT_DEVICE_ACTIVITY = False
LOGGER_PRINT_CSR_REGISTER_ACTIVITY = False

LOGGER_REPORT_TYPE = ReportType.LONG_REPORT
# LOGGER_REPORT_TYPE = ReportType.SHORT_REPORT
# LOGGER_REPORT_TYPE = ReportType.C_EMU_REPORT
TTY_OUTPUT_ENABLED = True

# Generate CPU state output for all instructions
if 0:
    START_TRACEOUT_AT_INSTRUCTION_NO = 0
    LOGGER_REPORT_TYPE = ReportType.C_EMU_REPORT
    TTY_OUTPUT_ENABLED = False

# TEMP
if 1:
    START_TRACEOUT_AT_INSTRUCTION_NO = 39690300 # 39510000 # 39691180
    EXIT_EMULATOR_AT_INSTRUCTION_NO  = False
    # LOGGER_REPORT_TYPE = ReportType.C_EMU_REPORT
    LOGGER_REPORT_TYPE = ReportType.SHORT_REPORT
    # BREAKPOINT_AT_INSTRUCTION_NO = 3376954
    TTY_OUTPUT_ENABLED = True
    #LOGGER_PRINT_CSR_REGISTER_ACTIVITY = True
