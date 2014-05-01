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
from threading import Thread, Lock
from random import randint

screen = None

l = Lock()


# Drop
# Light-up
# Disappear

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

def draw_fn(y, x, msg, color=None):
    try:
        if color is None:
            screen.addstr(y, x, msg)
        else:
            screen.addstr(y, x, msg, color)
    except:
        exit_curses()
        sys.exit(0)

def draw_frame(frame, x, y, mask):
    for n in mask:
        with l:
            draw_fn(y + n, x, frame[n], curses.color_pair(5))

def debug(msg):
    log = 'curses-log'
    with open(log, 'a') as f:
        f.write(str(msg) + '\n')

def main(duration):
    h, w = screen.getmaxyx()

    face = [
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
"                                            "]


    face_width = 0
    for line in face:
        if len(line) > face_width:
            face_width = len(line)

    to_display = range(0, len(face))
    mask = []

    facex = (w - face_width) / 2
    facey = (h - len(face)) / 2

    tick = 0.025
    elapsed = 0

    drops = []
    while True:
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

        if elapsed > duration:
            if len(to_display) > 0:
                n = randint(0, len(to_display)-1)
                mask.append(to_display[n])
                del to_display[n]

            draw_frame(face, facex, facey, mask)

        screen.refresh()

        time.sleep(tick)
        elapsed += tick

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
    if len(sys.argv) > 1:
        duration = int(sys.argv[1])
    try:
        status = main(duration)
    finally:
        exit_curses()

    sys.exit(status)
