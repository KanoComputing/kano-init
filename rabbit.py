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

from random import randint

screen = None


def draw_fn(y, x, msg, color=None):
    try:
        if color is None:
            screen.addstr(y, x, msg)
        else:
            screen.addstr(y, x, msg, color)
    except:
        exit_curses()
        raise


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


def debug(msg):
    log = 'curses-log'
    with open(log, 'a') as f:
        f.write(str(msg) + '\n')



def draw_frame(frame, x, y, animation_width):
    """
        Draw a sigle frame to a curses screen

        The frame is drawn from the [x,y] coordinates.
    """

    h, w = screen.getmaxyx()

    left_clip = 0
    if x < 0:
        left_clip = abs(x)
        x = 0

    right_clip = 0
    if (x + animation_width) >= w:
        right_clip = (x + animation_width) - w
        if right_clip > animation_width:
            right_clip = animation_width

    n = 0
    for line in frame:
        clipped_line = line[left_clip:(animation_width - right_clip)]
        if len(clipped_line) > 0:
            draw_fn(y + n, x, clipped_line)
            n += 1

def main(max_cycles):
    res_dir = "."
    if not os.path.isdir("ascii_art"):
        res_dir = "/usr/share/kano-init"

    ascii_art_dir = res_dir + "/ascii_art"

    # preload all parts of the animation
    rabbit_lr = load_animation(ascii_art_dir + "/rabbit-animation.txt")
    rabbit_w = animation_width(rabbit_lr)
    rabbit_h = animation_height(rabbit_lr)

    rabbit_rl = load_animation(ascii_art_dir + "/rabbit-animation-reversed.txt")

    h, w = screen.getmaxyx()

    # screen centre
    cx, cy = w/2, h/2

    startx = -rabbit_w
    starty = randint(0, h - rabbit_h - 1)

    rabbit = rabbit_lr

    frame = 0
    offsetx = offsety = 0
    offset_diff = 10
    cycle = 0
    while True:
        n = 0
        while n < rabbit_h:
            draw_fn(starty + n, 0, " "*(w-1))
            n += 1

        draw_frame(rabbit[frame], startx + offsetx, starty, rabbit_w)
        frame += 1
        if frame >= len(rabbit):
            frame = 0

        offsetx += offset_diff

        if max_cycles == 0 and startx + offsetx >= (cx - rabbit_w/2):
            time.sleep(0.5)
            break
        elif startx + offsetx > w:
            rabbit = rabbit_rl
            offset_diff = -offset_diff
            starty = randint(0, h - rabbit_h - 1)
            cycle += 1
            if cycle >= max_cycles:
                break
        elif startx + offsetx < -rabbit_w:
            rabbit = rabbit_lr
            offset_diff = -offset_diff
            starty = randint(0, h - rabbit_h - 1)
            cycle += 1
            if cycle >= max_cycles:
                break

        screen.refresh()

        time.sleep(0.15)

    return 0


def init_curses():
    global screen

    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    screen.keypad(1)
    curses.curs_set(0)


def exit_curses():
    curses.curs_set(2)
    screen.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()


if __name__ == "__main__":
    init_curses()
    max_cycles = 3
    if len(sys.argv) > 1:
        max_cycles = int(sys.argv[1])
    try:
        status = main(max_cycles)
    finally:
        exit_curses()

    sys.exit(status)
