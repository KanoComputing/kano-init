#
# bomb.py
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
key = "startx"
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
        draw_fn(y + n, x, line)
        n += 1


def blink(duration, interval):
    """
        Blink the screen

        The `duration` parameter says how long will the blinking
        last. The `interval` argument controls the time between
        individual flashes. Both values are in seconds.
    """

    curses.curs_set(0)
    h, w = screen.getmaxyx()

    repeats = int((duration * 1.0) / interval)
    colour = 1
    for n in range(0, repeats):
        for y in range(0, h):
            draw_fn(y, 0, " " * (w - 1), curses.color_pair(colour))

        screen.refresh()

        colour = 2 if colour == 1 else 1
        time.sleep(interval)


def main(username):
    global keypos

    keypos = 0

    # Preload all parts of the animation in the memory.
    spark = load_animation(ASCII_RES_PATH + "/spark.txt")

    numbers = load_animation(ASCII_RES_PATH + "/numbers.txt")
    num_w = animation_width(numbers)

    bomb = load_animation(ASCII_RES_PATH + "/bomb.txt")
    bomb_w = animation_width(bomb)
    bomb_h = animation_height(bomb)

    msg1 = "Quick, %s, type " % username
    msg2 = "startx"
    msg3 = " to escape!"

    rv = 0

    h, w = screen.getmaxyx()

    # Determine the position of the bomb.
    startx = (w - bomb_w - num_w - 10) / 2
    starty = (h - bomb_h - 8) / 2

    # Position of the message.
    msgx = startx + (num_w + 10) / 2
    msgy = starty + bomb_h + 2

    # Determine the initial position of the cursor.
    cursorx = msgx + len(msg1 + msg2 + msg3) / 2 - 3
    cursory = msgy + 2

    # Initialize the bomb.
    draw_frame(bomb[0], startx, starty)

    x = msgx
    draw_fn(msgy, x, msg1)
    x += len(msg1)
    draw_fn(msgy, x, msg2, curses.color_pair(3))
    x += len(msg2)
    draw_fn(msgy, x, msg3)

    # Intitialise an auxiliary window for user input.
    win = curses.newwin(1, 8, cursory, cursorx)
    win.clear()
    win.timeout(125)

    cycle = 0
    spark_frame = 0
    numbers_frame = 0
    while True:
        # Animate the countdown
        if cycle % 8 == 0:
            draw_frame(numbers[numbers_frame],
                       startx + 10 + bomb_w, starty + (bomb_h / 2) + 4)

            numbers_frame += 1
            if numbers_frame >= len(numbers):
                # Countdown is over, blink the screen and restart
                # the animation from the beginning. 
                blink(1.0, 0.08)
                rv = 1
                break

        # Animate the spark
        draw_frame(spark[spark_frame], startx, starty)
        spark_frame += 1
        if spark_frame >= len(spark):
            spark_frame = 0

        # Refresh the screen
        screen.move(cursory, cursorx + keypos)
        screen.refresh()

        # Wait for user input, getch() will block for 125ms after which
        # the next frame of the animation will be drawn.
        before_sleep = time.time()
        c = win.getch(0, keypos)
        if c != curses.ERR and c > 0 and chr(c).lower() == key[keypos]:
            win.addstr(0, keypos, chr(c).lower())
            keypos += 1
            if keypos >= len(key):
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


def bomb(user="buddy"):
    rv = 1
    try:
        init_curses()
        rv = main(user)
    finally:
        shutdown_curses()

    return rv


if __name__ == "__main__":
    user = "buddy"
    if len(sys.argv) > 1:
        user = sys.argv[1]

    n = 0
    rv = 1
    while n < 20 and rv != 0:
        rv = bomb(user)
        n += 1

    sys.exit(rv)
