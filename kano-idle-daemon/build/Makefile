# Makefile
#
# Copyright (C) 2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Build file for kano-idle-daemon


CC = gcc
CFLAGS = -Wall


all:
	${CC} ${CFLAGS} ../src/kano-idle-daemon.c -o ../bin/kano-idle-daemon -L/usr/X11R6/lib/ -lX11 -lXext -lXss
