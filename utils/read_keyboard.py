
from platform import system

if system() == 'Windows':
    import msvcrt


def read_key_windows():
    if msvcrt.kbhit():
        return ord(msvcrt.getch())
    else:
        return 0xffffffff

def read_key():
    if system() == 'Windows':
        return read_key_windows()
    else:
        return 0xffffffff
