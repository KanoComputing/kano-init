#!/bin/sh

# autostart-kano-init.sh
#
# Copyright (C) 2013 Kano Computing Ltd.
# License:   http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# 0: Disabled
# 1: Name
# 2: Country
# 3: Email
# 4: Rabbit
# 5: Bomb

STAGE=0

if [ `id -u` -eq 0 -a "$STAGE" -gt 0 ]; then
    kano-init "$STAGE"
    kill -HUP $PPID
fi