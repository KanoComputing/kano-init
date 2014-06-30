#!/usr/bin/env python

# bomb.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Startx exercise
#

import os
import sys
import time
import curses
from threading import Thread, Lock

screen = None
key = "startx"
keypos = 0

l = Lock()


def draw_fn(y, x, msg, color=None):
    try:
        if color is None:
            screen.addstr(y, x, msg)
        else:
            screen.addstr(y, x, msg, color)
    except:
        exit_curses()
        sys.exit(0)


def user_input(cursorx, cursory):
    """
        Runs as a background thread to capture user input.

        Separate window is created just for the input.
        A global thread lock (l) is used for all calls to
        curses to avoid any mixups.
    """

    # Current position in the key phrase. Must be global so the
    # main thread can position the cursor correctly.
    global keypos

    # Avoids problems with the thread moving the cursor too early
    time.sleep(0.5)

    with l:
        win = curses.newwin(1, 8, cursory, cursorx)

    while True:
        c = win.getch(0, keypos)
        if c != curses.ERR and chr(c).lower() == key[keypos]:
            with l:
                win.addstr(0, keypos, chr(c).lower())
                win.refresh()
                keypos += 1
            if keypos >= len(key):
                return


def load_animation(path):
    """
        Loads an ASCII art animation

        The animation must be stored in a plain text file
        frame-by-frame. Each frame must be delimited by
        a line consiting only of '---'.

        Example:

            FRAME1
            ---
            FRAME2
            ---
            FRAME3
            ---
    """

    frames = []
    with open(path) as f:
        frame = []
        for line in f:
            line = line.strip("\n")
            if line == "---":
                frames.append(frame)
                frame = []
            else:
                frame.append(line)

        # Append the last frame
        if len(frame) > 0:
            frames.append(frame)

    return frames


def animation_width(animation):
    """ Determine the maximum frame width of an animation """

    width = 0
    for frame in animation:
        for line in frame:
            if len(line) > width:
                width = len(line)

    return width


def animation_height(animation):
    """ Determine the maximum frame height of an animation """

    height = 0
    for frame in animation:
        if len(frame) > height:
            height = len(frame)

    return height


def draw_frame(frame, x, y):
    """
        Draw a sigle frame to a curses screen

        The frame is drawn from the [x,y] coordinates.
    """

    n = 0
    for line in frame:
        with l:
            draw_fn(y + n, x, line)
        n += 1


def blink(duration, interval):
    """
        Blink the screen

        The `duration` parameter says how long will the blinking
        last. The `interval` argument controls the time between
        individual flashes. Both values are in seconds.
    """

    with l:
        # initialize colours for blinking
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_WHITE)

        curses.curs_set(0)
        h, w = screen.getmaxyx()

    repeats = int((duration * 1.0) / interval)
    colour = 1
    for n in range(0, repeats):
        for y in range(0, h):
            with l:
                draw_fn(y, 0, " " * (w - 1), curses.color_pair(colour))

        with l:
            screen.refresh()

        colour = 2 if colour == 1 else 1
        time.sleep(interval)


def main(username):
    res_dir = "."
    if not os.path.isdir("ascii_art"):
        res_dir = "/usr/share/kano-init"

    ascii_art_dir = res_dir + "/ascii_art"

    # preload all parts of the animation
    spark = load_animation(ascii_art_dir + "/spark.txt")

    numbers = load_animation(ascii_art_dir + "/numbers.txt")
    num_w = animation_width(numbers)

    bomb = load_animation(ascii_art_dir + "/bomb.txt")
    bomb_w = animation_width(bomb)
    bomb_h = animation_height(bomb)

    msg = "Quick, %s, type startx to escape!" % username

    with l:
        h, w = screen.getmaxyx()

    # position of the bomb
    startx = (w - bomb_w - num_w - 10) / 2
    starty = (h - bomb_h - 8) / 2

    # position of the message
    msgx = startx + (num_w + 10) / 2
    msgy = starty + bomb_h + 2

    # initial position of the cursor
    cursorx = msgx + len(msg) / 2 - 3
    cursory = msgy + 2

    # initialize the bomb
    draw_frame(bomb[0], startx, starty)
    with l:
        draw_fn(msgy, msgx, msg)

    # Start the thread for the input functionality
    t = Thread(target=user_input, args=(cursorx, cursory))
    t.daemon = True
    t.start()

    cycle = 0
    spark_frame = 0
    numbers_frame = 0
    while True:
        # animate the countdown
        if cycle % 8 == 0:
            draw_frame(numbers[numbers_frame],
                       startx + 10 + bomb_w, starty + (bomb_h / 2) + 4)

            numbers_frame += 1
            if numbers_frame >= len(numbers):
                blink(1.0, 0.08)
                return 1

        # animate the spark
        draw_frame(spark[spark_frame], startx, starty)

        spark_frame += 1
        if spark_frame >= len(spark):
            spark_frame = 0

        with l:
            screen.move(cursory, cursorx + keypos)
            screen.refresh()

        # stop when user enters the key
        if not t.is_alive():
            break

        cycle += 1
        time.sleep(0.125)

    return 0


def init_curses():
    global screen

    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    screen.keypad(1)


def exit_curses():
    curses.curs_set(2)
    screen.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()


if __name__ == "__main__":

    init_curses()
    user = "buddy"
    if len(sys.argv) > 1:
        user = sys.argv[1]
    try:
        status = main(user)
    finally:
        exit_curses()

    sys.exit(status)
