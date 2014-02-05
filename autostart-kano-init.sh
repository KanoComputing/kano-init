#!/bin/sh

# autostart-kano-init.sh
#
# Copyright (C) 2014 Kano Computing Ltd.
# License:   http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# stages:
# 1) User name
# 2) User email
# 3) White rabbit riddle
# 4) Startx
# 9) Reset

STAGE=0

if [ `id -u` -eq 0 -a "$STAGE" -gt 0 ]; then
    kano-init "$STAGE"
    kill -HUP $PPID
fi


