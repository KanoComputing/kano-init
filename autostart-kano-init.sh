#!/bin/sh

# autostart-kano-init.sh
#
# Copyright (C) 2014, 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

# If we are not on tty1, exit immediately,
# otherwise root would be "kano-inited" and unable to get a shell
# while kano-init is in username-stage.
#
if [ `tty` != "/dev/tty1" ]; then
	exit 0
fi

STATUS_FILE="/var/cache/kano-init/status.json"

if [ `id -u` -eq 0 -a "`json-get $STATUS_FILE stage`" != "disabled" ]; then
    kano-init boot
    kill -HUP $PPID
fi
