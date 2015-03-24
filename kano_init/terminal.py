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

SPEED_FACTOR = 1

def typewriter_echo(string):
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


def _write_flush(string):
    sys.stdout.write(string)
    sys.stdout.flush()


if __name__ == '__main__':
    typewriter_echo("Hello there Mr. Anderson, how are you today?")
    typewriter_echo("Woooooooooooooot? No, I don't mean that.")
