
from platform import system

# https://stackoverflow.com/questions/2408560/non-blocking-console-input
# https://www.darkcoding.net/software/non-blocking-console-io-is-not-possible/

if system() == 'Windows':
    import msvcrt

    def read_key():
        if msvcrt.kbhit():
            return ord(msvcrt.getch())
        else:
            return 0xffffffff

    def tty_prepare():
        import os
        # Apparently this is how to put "cmd" interpreter into VT100 mode
        # Otherwise we will see VT100 escape sequences when running from cmd
        os.system("")

    def tty_release():
        pass

elif system() == "Linux":
    import sys
    import select
    import tty
    import termios

    old_settings = None

    def InputIsAvailable():
            return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

    def read_key():
        # We first check if Input is available, so that stdin.read does not block waiting on input
        if InputIsAvailable():
            return ord(sys.stdin.read(1))
        else:
            return 0xffffffff

    def tty_prepare():
        global old_settings
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        pass

    def tty_release():
        global old_settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        pass
