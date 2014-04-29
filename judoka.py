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

cursorx = 0
cursory = 0

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


def debug(msg):
    log = 'curses-log'
    with open(log, 'a') as f:
        f.write(str(msg) + '\n')

def typewriter(text, startx, starty, pos):
    global cursorx, cursory

    x = y = 0

    for line in text:
        if pos >= len(line):
            pos -= len(line)
            y += 1
        else:
            x = pos
            break

    if y >= len(text):
        return True

    with l:
        draw_fn(starty + y, startx + x, text[y][x])

    cursorx = startx + x + 1
    cursory = starty + y

    return False

def main(username):
    global cursorx, cursory

    debug("---")

    res_dir = "."
    if not os.path.isdir("ascii_art"):
        res_dir = "/usr/share/kano-init"

    ascii_art_dir = res_dir + "/ascii_art"

    # preload all parts of the animation
    judoka = load_animation(ascii_art_dir + "/judoka.txt")
    judoka_w = animation_width(judoka)
    judoka_h = animation_height(judoka)

    msg = "Quick, %s, type startx to escape!" % username
    console_text = ["Hi, I'm KANO. Thanks for bringing me to life.",
                    " ",
                    "What should I call you?"]

    with l:
        h, w = screen.getmaxyx()

    # position of the judoka
    startx = (w - judoka_w - 10 - 50) / 2
    starty = (h - judoka_h) / 2

    # position of the console
    consolex = (startx + judoka_w + 10)
    consoley = starty + 2

    cycle = 0
    judoka_frame = 0
    judoka_wink = 0

    cursorx = consolex
    cursory = consoley

    text_pos = 0
    t = None
    while True:
        if cycle % 8 == 0:
            # animate the judoka
            draw_frame(judoka[judoka_frame], startx, starty)

            judoka_frame += 1
            if judoka_frame >= len(judoka) - 1:
                judoka_frame = 0

            judoka_wink += 1
            if judoka_wink == 10:
                judoka_frame = len(judoka) - 1
                judoka_wink = 0

        done = typewriter(console_text, consolex, consoley, text_pos)
        if not done:
            text_pos += 1
        else:
            if not t:
                cursorx = consolex
                cursory = consoley + 4

                # Start the thread for the input functionality
                t = Thread(target=user_input, args=(cursorx, cursory))
                t.daemon = True
                t.start()

        with l:
            screen.move(cursory, cursorx + keypos)
            screen.refresh()

        # stop when user enters the key
        if t and not t.is_alive():
            break

        cycle += 1
        time.sleep(0.06)#0.125)

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
