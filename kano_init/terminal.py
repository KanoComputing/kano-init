#
# terminal.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Write to terminal in a Matrix-style
#
# Params:
#   $1: Sring to be printed
#   $2: Wait time at the end of the line (optional)
#   $3: Number of line breaks at the end (optional)
#   $4: Whether there is padding at the start of the line (0, 1 or X) (optional)
#   $5: Whether there is padding at the start of the next line (1 or 0) (optional)
#   $6: Number of line breaks at the start (optional)
#

import sys
import time
import termios
import atexit


original_state = None
SPEED_FACTOR = 1


def restore_original_state():
    if original_state:
        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSADRAIN, original_state)


def save_original_state():
    global original_state

    if not original_state:
        fd = sys.stdin.fileno()
        original_state = termios.tcgetattr(fd)

        atexit.register(restore_original_state)


# Store the original state of the terminal and make sure we restore it
save_original_state()


def typewriter_echo(string):
    set_echo(False)

    for c in string:
        if c == ' ':
            # Sleep for a little longer between words
            time.sleep(0.06 * SPEED_FACTOR)
        elif c in ['.', ',', '?', '!']:
            # The sleep is a little longer for punctuation
            time.sleep(0.04 * SPEED_FACTOR)
        else:
            time.sleep(0.02 * SPEED_FACTOR)

        _write_flush(c)

    time.sleep(0.25 * SPEED_FACTOR)
    _write_flush('\n')

    set_echo(True)
    discard_input()


def _write_flush(string):
    sys.stdout.write(string)
    sys.stdout.flush()


def set_echo(enabled=True):
    fd = sys.stdin.fileno()
    attrs = termios.tcgetattr(fd)

    if enabled:
        attrs[3] = attrs[3] | termios.ECHO
    else:
        attrs[3] = attrs[3] & ~termios.ECHO

    termios.tcsetattr(fd, termios.TCSADRAIN, attrs)


def discard_input():
    termios.tcflush(sys.stdin.fileno(), termios.TCIOFLUSH)


if __name__ == '__main__':
    typewriter_echo("Hello there Mr. Anderson, how are you today?")
    typewriter_echo("Woooooooooooooot? No, I don't mean that.")
