#
# ascii_image.py
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The 'startx' exercise with the bomb.
#
# TODO: Needs a LOT of refactoring.
#

import sys
import time
import curses

from kano_init.paths import ASCII_RES_PATH

screen = None


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


def main(image_file, length):

    image = load_image(ASCII_RES_PATH + "/" + image_file)
    image_w = image_width(image)
    image_h = len(image)

    h, w = screen.getmaxyx()

    # Determine the position of the image.
    startx = (w - image_w) / 2
    starty = (h - image_h) / 2

    # Draw the image.
    draw_image(image, startx, starty)
    screen.refresh()
    curses.flushinp()
    time.sleep(length)


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

        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)


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
    return h >= 40 and w >= 70


def ascii_image(image_file, length):
    try:
        init_curses()

        if not is_screen_big_enough():
            raise EnvironmentError("Screen too small")

        main(image_file, length)
    finally:
        shutdown_curses()
