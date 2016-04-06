#
# loading.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
#

import sys
import time
import curses

from kano_init.paths import ASCII_RES_PATH

screen = None

hexcode = """
003837c: 00001000 00100000 10000000 . ...~
0038382: 00010110 00100000 01000000 . @...
0038388: 11010010 00110111 00000100 .7..@.
003838e: 00000001 00000100 00010000 ...@..
0038394: 00000100 00010000 01000000 ..@...
003839a: 00010000 01000000 00000000 .@....
00383a0: 10110000 11000000 10101101 ...r..
00383a6: 00101000 00000100 01110011 (.s.Q.
003842a: 00010000 01000000 11000000 .@....
0038430: 10001000 00111110 00011110 .>.\..
0038436: 00000000 00000010 00001000 ... ..
003843c: 00000010 00001000 00100000 .. ...
0038442: 00001000 00100000 10000000 . ....
0038448: 00100000 00010000 01011110  .^.^.
003844e: 01100110 10111101 10001110 f.....
0038454: 11011000 01011000 00001011 .X..,.
003845a: 11010011 01111111 00011111 ....mv"""


def draw_fn(y, x, msg, color=None):
    try:
        if color is None:
            screen.addstr(y, x, msg)
        else:
            screen.addstr(y, x, msg, color)
    except:
        shutdown_curses()
        sys.exit(0)


def load_image(path):
    """
        Loads an ASCII art image from a file
    """
    image = []
    with open(path) as f:
        for line in f:
            line = line.strip("\n")
            image.append(line)

    return image


def image_width(image):
    """ Determine the maximum width of the image """
    width = 0
    for line in image:
        if len(line) > width:
            width = len(line)

    return width


def draw_image(image, x, y, color=None):
    """
        Draw the image to a curses screen

        The frame is drawn from the [x,y] coordinates.
    """
    n = 0
    for line in image:
        draw_fn(y + n, x, line, color)
        n += 1


def main():

    h, w = screen.getmaxyx()

    # Loading title
    loading_title = load_image(ASCII_RES_PATH + "/loading.txt")
    loading_x = (w - image_width(loading_title)) / 2
    loading_y = 7
    # Scrolling hex code
    code = hexcode.splitlines()
    code_x = (w - len(code[1])) / 2
    code_y = len(code) + (loading_y + len(loading_title) + 2)

    cycle = 0
    while cycle < len(code):
        # Draw blinking loading title
        if cycle % 2 == 0:
            draw_image(loading_title, loading_x, loading_y,
                       curses.color_pair(1))
        else:
            for y in range(0, len(loading_title)):
                draw_fn(loading_y + y, 0, " " * (w - 1), curses.color_pair(2))

        # Draw lines of hex code
        y = code_y
        for i in range(0, cycle):
            draw_fn(y, code_x, code[i])
            y += 1
        code_y -= 1

        time.sleep(0.7)
        screen.refresh()
        curses.flushinp()

        cycle += 1


def init_curses():
    global screen

    screen = curses.initscr()
    screen.clear()
    screen.refresh()
    curses.noecho()
    curses.cbreak()
    screen.keypad(1)

    curses.start_color()
    if curses.has_colors():
        curses.use_default_colors()

        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLACK)


def shutdown_curses():
    curses.curs_set(2)
    screen.keypad(0)
    screen.clear()
    screen.refresh()
    curses.echo()
    curses.nocbreak()
    curses.endwin()


def is_screen_big_enough():
    h, w = screen.getmaxyx()
    return h >= 38 and w >= 70


def loading():
    try:
        init_curses()

        if not is_screen_big_enough():
            raise EnvironmentError('Screen too small')

        main()
    finally:
        shutdown_curses()
        # ignore exception and allow init to proceed
        return
