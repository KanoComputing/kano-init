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

TOP_PADDING = 4
LEFT_PADDING = 9

def restore_original_state():
    if sys.stdin.isatty() and original_state:
        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSADRAIN, original_state)


def save_original_state():
    global original_state

    if sys.stdin.isatty() and not original_state:
        fd = sys.stdin.fileno()
        original_state = termios.tcgetattr(fd)

        atexit.register(restore_original_state)


# Store the original state of the terminal and make sure we restore it
save_original_state()


def clear_screen(top_padding=True):
    sys.stderr.write("\x1b[2J\x1b[H")
    if top_padding:
        print TOP_PADDING * '\n'
    sys.stderr.flush()


def typewriter_echo(string, sleep=0, trailing_linebreaks=1):
    set_echo(False)

    write_flush(LEFT_PADDING * ' ')

    for c in string:
        if c == ' ':
            # Sleep for a little longer between words
            time.sleep(0.075 * SPEED_FACTOR)
        elif c in ['.', ',', '?', '!']:
            # The sleep is a little longer for punctuation
            time.sleep(0.05 * SPEED_FACTOR)
        else:
            time.sleep(0.025 * SPEED_FACTOR)

        write_flush(c)

    time.sleep(sleep + 0.3 * SPEED_FACTOR)
    write_flush(trailing_linebreaks * '\n')

    set_echo(True)
    discard_input()


def write_flush(string):
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

def user_input(prompt):
    typewriter_echo(prompt, trailing_linebreaks=0)
    discard_input()
    return raw_input()


def discard_input():
    termios.tcflush(sys.stdin.fileno(), termios.TCIOFLUSH)


if __name__ == '__main__':
    typewriter_echo("Hello!")
    typewriter_echo("I'm KANO. Thanks for bringing me to life.")
