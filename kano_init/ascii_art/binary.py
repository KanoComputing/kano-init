#
# binary.py
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
#

import sys
import time
import curses
from random import randint

screen = None
keypos = 0


def draw_fn(y, x, msg, color=None):
    try:
        if color is None:
            screen.addstr(y, x, msg)
        else:
            screen.addstr(y, x, msg, color)
    except:
        shutdown_curses()
        sys.exit(0)


def main(username):
    global keypos

    keypos = 0

    msg1 = "These switches speak in 1s and 0s. This is called binary code."
    msg2 = "Press [ENTER] to keep exploring."

    rv = 0

    h, w = screen.getmaxyx()
    max_row = 10
    max_column = 10

    # Determine the position of the grid.
    startx = (w - (max_column * 4)) / 2
    starty = (h - (max_row * 2)) / 2

    # Position of message1 (make sure is > 0)
    msg1x = max(0, (w - len(msg1)) / 2)
    msg1y = starty - 2
    # Draw messsage 1
    draw_fn(msg1y, msg1x, msg1)

    # Position of message2 (make sure is > 0)
    msg2x = max(0, (w - len(msg2)) / 2)
    msg2y = starty + (max_row * 2) + 2
    # Draw messsage 2
    draw_fn(msg2y, msg2x, msg2)

    # Determine the initial position of the cursor.
    cursorx = w / 2
    cursory = msg2y + 2

    # Intitialise an auxiliary window for user input.
    win = curses.newwin(1, 8, cursory, cursorx)
    win.clear()
    win.timeout(125)

    cycle = 0
    while True:
        # Draw the "switches"
        y = starty
        x = startx
        for row in range(0, max_row):
            # Draw row of random 0's and 1's
            for column in range(0, max_column):
                r = randint(0, 1)
                if r == 0:
                    s = "0"
                    color = curses.color_pair(2)  # RED
                else:
                    s = "1"
                    color = curses.color_pair(1)  # GREEN
                s = ("0" if r else "1")
                draw_fn(y, x, s, color)
                x = x + 1
                if column < max_column - 1:
                    draw_fn(y, x, " - ")
                    x = x + 3
            # Draw row of | - |
            if row < max_row - 1:
                x = startx
                y = y + 1
                s = '| '
                for i in range(0, max_column - 1):
                    s = s + "- | "
                draw_fn(y, x, s)
                # Update for next row
                x = startx
                y = y + 1

        # Refresh the screen
        screen.move(cursory, cursorx + keypos)
        screen.refresh()

        # Wait for user input, getch() will block for 125ms after which
        # the next frame of the animation will be drawn.
        before_sleep = time.time()
        c = win.getch(0, keypos)
        if c != curses.ERR and c > 0:
            break
        slept_for = time.time() - before_sleep
        if slept_for < 0.125:
            time.sleep(0.125 - slept_for)
        curses.flushinp()

        cycle += 1

    return rv


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
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)


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


def binary(user="buddy"):
    rv = 1
    try:
        init_curses()

        if not is_screen_big_enough():
            raise EnvironmentError('Screen too small')

        rv = main(user)
    finally:
        shutdown_curses()

    return rv
