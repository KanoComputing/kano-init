#
# terminal.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Write to terminal in a Matrix-style
#
# TODO: This could be useful as kano.terminal but it needs
#       a bit more work before it can be moved there.


import sys
import time
import termios
import atexit
import subprocess

original_state = None
SPEED_FACTOR = 1

TOP_PADDING = 0
LEFT_PADDING = 0


def set_overscan():
    try:
        otxt = subprocess.check_output('fbset')
        h = None
        v = None
        for line in otxt.split('\n'):
            if 'geometry' in line:
                parts = line.split()
                h = str(int(parts[1])/8)
                v = str(int(parts[2])/8)
        if h and v:
            subprocess.check_call(['overscan', h, h, v, v])
    except:
        pass


def reset_overscan():
    try:
        subprocess.check_call(['overscan', '0', '0', '0', '0'])
    except:
        pass


def restore_original_state():
    if sys.stdin.isatty() and original_state:
        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSADRAIN, original_state)
        reset_overscan()


def save_original_state():
    global original_state

    if sys.stdin.isatty() and not original_state:
        fd = sys.stdin.fileno()
        original_state = termios.tcgetattr(fd)
        set_overscan()
        atexit.register(restore_original_state)


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
    sys.stdout.write(string)  # TODO: set encoding to UTF-8
    sys.stdout.flush()


def set_echo(enabled=True):
    if not sys.stdin.isatty():
        return

    fd = sys.stdin.fileno()
    attrs = termios.tcgetattr(fd)

    if enabled:
        attrs[3] = attrs[3] | termios.ECHO
    else:
        attrs[3] = attrs[3] & ~termios.ECHO

    termios.tcsetattr(fd, termios.TCSADRAIN, attrs)


def set_control(enabled=True):
    if not sys.stdin.isatty():
        return

    fd = sys.stdin.fileno()
    attrs = termios.tcgetattr(fd)

    if enabled:
        attrs[0] = attrs[0] | termios.IXON
        attrs[0] = attrs[0] | termios.IXOFF

        attrs[6][termios.VSUSP] = '\x1a'
        attrs[6][termios.VQUIT] = '\x1c'
        attrs[6][termios.VKILL] = '\x15'
        attrs[6][termios.VINTR] = '\x03'
        attrs[6][termios.VEOF] = '\x04'
    else:
        attrs[0] = attrs[0] & ~termios.IXON
        attrs[0] = attrs[0] & ~termios.IXOFF

        attrs[6][termios.VSUSP] = '\x00'
        attrs[6][termios.VQUIT] = '\x00'
        attrs[6][termios.VKILL] = '\x00'
        attrs[6][termios.VINTR] = '\x00'
        attrs[6][termios.VEOF] = '\x00'

    termios.tcsetattr(fd, termios.TCSADRAIN, attrs)


def user_input(prompt):
    typewriter_echo(prompt, trailing_linebreaks=0)
    discard_input()
    try:
        return raw_input()
    except EOFError:
        return ''


def discard_input():
    termios.tcflush(sys.stdin.fileno(), termios.TCIOFLUSH)
