#!/usr/bin/env python

# judoka.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Startx exercise
#

import re
import os
import sys
import time
import curses
from threading import Thread, Lock

screen = None
keypos = 0
user_name = ""
error = ""

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
    global user_name

    # Avoids problems with the thread moving the cursor too early
    time.sleep(0.5)

    with l:
        win = curses.newwin(1, 45, cursory, cursorx)

        curses.echo()

    user_name = win.getstr(0,0,25)

def validate(user_name):
    global error
    if len(user_name) == 0:
        error = "Type a cool name."
        return False
    elif re.search("[^a-zA-Z0-9]", user_name):
        error = "Just one word, letters or numbers! Try again."
        return False

    with open("/etc/passwd") as f:
        for line in f:
            if re.match("^{}\:".format(user_name), line) != None:
                error = "This one is already taken! Try again."
                return False

    return True

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

    with l:
        screen.move(starty + y, startx + x + 1)

    return False

def main():
    global cursorx, cursory

    res_dir = "."
    if not os.path.isdir("ascii_art"):
        res_dir = "/usr/share/kano-init"

    ascii_art_dir = res_dir + "/ascii_art"

    # preload all parts of the animation
    judoka = load_animation(ascii_art_dir + "/judoka.txt")
    judoka_w = animation_width(judoka)
    judoka_h = animation_height(judoka)

    console_text = ["Hello!", "",
                    "I'm KANO. Thanks for bringing me to life.", "",
                    "What should I call you?", "",
                    "> "]

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

    text_pos = 0
    t = None

    # 1: writing message
    # 2: user input
    # 3: error               <---,
    # 4: repeated user input  ---'
    state = 1

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

        debug(state)
        if state == 1:
            if typewriter(console_text, consolex, consoley, text_pos):
                state = 2
                text_pos = 0
                curses.curs_set(0)
            else:
                text_pos += 1
        elif state == 2:
            if not t:
                # Start the thread for the input functionality
                t = Thread(target=user_input, args=(consolex+2, consoley+6))
                t.daemon = True
                t.start()
            else:
                if not t.is_alive():
                    if (validate(user_name)):
                        debug(user_name)
                        break
                    else:
                        state = 3
                        t = None
        elif state == 3:
            if typewriter([error], consolex, consoley+8, text_pos):
                state = 4
                text_pos = 0
                draw_fn(consoley+6, consolex, "> " + " "*50)
            else:
                text_pos += 1
        elif state == 4:
            if not t:
                # Start the thread for the input functionality
                t = Thread(target=user_input, args=(consolex+2, consoley+6))
                t.daemon = True
                t.start()
                curses.curs_set(0)
            else:
                if not t.is_alive():
                    if (validate(user_name)):
                        break
                    else:
                        state = 3
                        t = None
                        draw_fn(consoley+8, consolex, "> " + " "*50)

        with l:
            screen.refresh()

        cycle += 1
        time.sleep(0.05)#0.125)

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
    try:
        status = main()
    finally:
        exit_curses()

    sys.exit(status)
