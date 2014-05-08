#!/usr/bin/env python

# bomb.py
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
        sys.exit(0)


class Drop(object):
    def __init__(self, posx=0, posy=0, drop_length=50,
                 cycles_per_character=1, c1=None, c2=None):
        self._length = drop_length

        self._cycle = 0

        self._posx = posx
        self._posy = posy
        self._charpos = 0

        self._cycles_per_char = cycles_per_character

        self._phase = 1
        self._colour1 = c1
        self._colour2 = c2

    def draw_next(self):
        if self._phase == 1:
            if self._charpos < self._length:
                self._phase_one()
                return False
            else:
                self._charpos = 0
                self._phase = 2

        if self._phase == 2:
            if self._charpos < self._length:
                self._phase_two()
                return False
            else:
                self._charpos = 0
                self._phase = 3

        if self._phase == 3:
            if self._charpos < self._length:
                self._phase_three()
                return False

        return True

    def _phase_one(self):
        if self._cycle % self._cycles_per_char == 0:
            draw_fn(self._posy + self._charpos, self._posx,
                          chr(randint(97, 122)), self._colour1)
            self._charpos += 1

            if self._charpos < self._length-1:
                draw_fn(self._posy + self._charpos, self._posx,
                        chr(randint(97, 122)), 4)

        self._cycle += 1

    def _phase_two(self):
        if self._cycle % self._cycles_per_char == 0:
            draw_fn(self._posy + self._charpos, self._posx,
                          chr(randint(65, 90)), self._colour2)
            self._charpos += 1

        self._cycle += 1

    def _phase_three(self):
        if self._cycle % self._cycles_per_char == 0:
            draw_fn(self._posy + self._charpos, self._posx, ' ')
            self._charpos += 1

        self._cycle += 1

    def force_phase_three(self):
        if self._phase != 3:
            if self._phase == 1:
                self._length = self._charpos + 1
            self._charpos = 0
            self._phase = 3
            self._cycles_per_char = 1


class Face(object):
    _face = [
        "                                            ",
        "               ?KKKKKKKKKKKKKK~             ",
        "            KKKKKK$.        $KKKKD=         ",
        "         ,KKKKI                KKKK:        ",
        "       ~KKKK                     7KKK       ",
        "      KKKK                        .KKK      ",
        "     KKKKKK,                        KK8     ",
        "   .KKK  OKKK                       .KK.    ",
        "  .KKK    KKKKK.                     8KK.   ",
        "  KKK    KKK KKKK=                    KK.   ",
        "  KK.   .KK.   KKKKK                  KKK.  ",
        "  KK.   KKK       KKKKKKK             IKK.  ",
        "  KK. DKKK           KKKKKKKKKK        KK.  ",
        "  KK?KKK                   KKKKKKKK    KK.  ",
        "  DKKK8      KK=           .KK..KKKKK .KK~  ",
        "  .KKKZ     KKKK           ?KKK.   KKK:KK   ",
        "   .KKK                             ?KKKK.  ",
        "    .KK?                            8KKKK.  ",
        "     IKK        KKKKKKKKKKK.        KKKK.   ",
        "      KKK.      DKK     KKK        KKK K    ",
        "       KKK.      KKKKIKKKK       :KKK       ",
        "        DKKK      IKKKKK$      .KKK$        ",
        "          KKKK                KKKK          ",
        "           .KKKKKK        KKKKKK            ",
        "              .DKKKKKKKKKKKKD               ",
        "                                            "
    ]

    def __init__(self, x=None, y=None, colour=None):
        h, w = screen.getmaxyx()
        if x:
            self._x = x
        else:
            face_width = 0
            for line in self._face:
                if len(line) > face_width:
                    face_width = len(line)

            self._x = (w - face_width) / 2

        if y:
            self._y = y
        else:
            self._y = (h - len(self._face)) / 2

        self._colour = colour
        self._pending_lines = range(0, len(self._face))
        self._mask = []


    def draw_next(self):
        if len(self._pending_lines) > 0:
            n = randint(0, len(self._pending_lines)-1)
            self._mask.append(self._pending_lines[n])
            del self._pending_lines[n]

        for n in self._mask:
            draw_fn(self._y + n, self._x, self._face[n], self._colour)


def debug(msg):
    log = 'curses-log'
    with open(log, 'a') as f:
        f.write(str(msg) + '\n')

def main(duration, show_face):
    h, w = screen.getmaxyx()

    drops = []

    if show_face:
        face = Face(None, None, curses.color_pair(5))

    tick = 0.025
    elapsed = 0
    #started_at = time.time()
    while True:
        #elapsed = time.time() - started_at
        elapsed += tick
        if elapsed < duration:
            length = randint(5,h-1)
            xpos = randint(0, w-1)
            ypos = randint(0, h-length-1)
            drop = Drop(xpos, ypos, length, randint(1, 2),
                        curses.color_pair(randint(1,3)),
                        curses.color_pair(randint(1,3)))
            drops.append(drop)

            length = randint(5,h-1)
            xpos = randint(0, w-1)
            ypos = randint(0, h-length-1)
            drop = Drop(xpos, ypos, length, randint(1, 2),
                        curses.color_pair(randint(1,3)),
                        curses.color_pair(randint(1,3)))
            drops.append(drop)
        else:
            for drop in drops:
                drop.force_phase_three()

        if len(drops) == 0:
            break

        i = 0
        while i < len(drops):
            drop = drops[i]
            done = drop.draw_next()
            if done:
                del drops[i]
            i += 1

        if show_face and elapsed > duration:
            face.draw_next()

        screen.refresh()

        time.sleep(tick)

    if show_face:
        time.sleep(1)

    return 0


def init_curses():
    global screen

    screen = curses.initscr()
    curses.curs_set(0)
    curses.noecho()
    curses.cbreak()
    screen.keypad(1)

    if curses.has_colors():
        curses.start_color()
        if curses.can_change_color():
            curses.init_color(curses.COLOR_GREEN, 1000, 517, 165)
            curses.init_color(curses.COLOR_BLUE, 909, 533, 35)
            curses.init_color(curses.COLOR_CYAN, 611, 529, 419)
            curses.init_color(curses.COLOR_WHITE, 1000, 905, 541)
            curses.init_color(curses.COLOR_RED, 1000, 1000, 1000)

            curses.init_pair(1, curses.COLOR_GREEN, 0)
            curses.init_pair(2, curses.COLOR_BLUE, 0)
            curses.init_pair(3, curses.COLOR_CYAN, 0)
            curses.init_pair(4, curses.COLOR_WHITE, 0)
            curses.init_pair(5, curses.COLOR_RED, 0)
        else:
            curses.use_default_colors()

            curses.init_pair(1, curses.COLOR_GREEN, 0)
            curses.init_pair(2, curses.COLOR_BLUE, 0)
            curses.init_pair(3, curses.COLOR_CYAN, 0)
            curses.init_pair(4, curses.COLOR_WHITE, 0)
            curses.init_pair(5, curses.COLOR_RED, 0)

def exit_curses():
    curses.curs_set(2)
    screen.keypad(0)
    curses.echo()
    curses.nocbreak()
    curses.endwin()


if __name__ == "__main__":
    init_curses()

    duration = 10
    show_face = False

    if len(sys.argv) > 1:
        duration = int(sys.argv[1])
    if len(sys.argv) > 2:
        show_face = (sys.argv[2] == "yes")

    try:
        status = main(duration, show_face)
    finally:
        exit_curses()

    sys.exit(status)
