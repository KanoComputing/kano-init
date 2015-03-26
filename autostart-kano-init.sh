#!/bin/sh

# autostart-kano-init.sh
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

STATUS_FILE="/var/cache/kano-init/status.json"

if [ `id -u` -eq 0 -a "`json-get $STATUS_FILE stage`" != "disabled" ]; then
    kano-init boot
    kill -HUP $PPID
fi
