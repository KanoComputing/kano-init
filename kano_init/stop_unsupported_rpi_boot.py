# stop_unsupported_rpi_boot.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The main functionality of the stop-unsupported-rpi-boot script.


import os
import time

from kano.utils.shell import run_cmd
from kano.utils.hardware import is_model_a, is_model_a_plus, is_model_b_beta, \
    is_model_b, is_model_b_plus, is_model_zero, is_model_zero_w

from kano_init.return_codes import RC


def is_unsupported_rpi():
    """Check if the Raspberry Pi board model is supported under Kano OS."""

    # The order of checks here is done Descending by Most Likely Model.
    return (
        is_model_b_plus() or is_model_b_beta() or is_model_b() or
        is_model_a() or is_model_a_plus() or
        is_model_zero() or is_model_zero_w()
    )


def sysrq_power_off():
    """Turn off the Raspberry Pi during very early boot process.

    This function requires root permissions.
    """

    # Safety check: Do not trigger a reboot if the filesystem has been
    # mounted as read/write to avoid potentially corrupting the SD card.
    out, err, rc = run_cmd('/bin/mount | /bin/grep "on / " | /bin/grep "ro"')
    if rc != 0:
        return

    with open('/proc/sys/kernel/sysrq', 'a') as sysrq:
        sysrq.write('1')

    with open('/proc/sysrq-trigger', 'a') as sysrq_trigger:
        sysrq_trigger.write('o')


def print_tty(text, console_tty='/dev/tty1'):
    """Helper function to print text to /dev/tty1.

    Args:
        text (str): Message to print to the console.
    """

    with open(console_tty, 'a') as tty:
        tty.write(text.encode('utf8'))


def main(args):
    """The main functionality of the stop-unsupported-rpi-boot script.

    The ``args`` are described in the executable docstring.

    Returns:
        int: The return code of the binary
    """

    if os.getuid() != 0:
        return RC.WRONG_PERMISSIONS

    if not args['--no-detect'] and not is_unsupported_rpi():
        return RC.SUCCESS

    # Prepare the console and screen to show a console message.
    run_cmd('/bin/setupcon')
    # TODO: Change this to `systemctl stop kano-boot-splash` when ready.
    run_cmd('kano-stop-splash boot')
    # Clear the console screen.
    print_tty('\033\0143')

    # TODO: This string is marked with N_() because the text printed to the
    # console which needs a utf8 font. When that is supported, just switch
    # to _().
    print_tty(N_(
        "Sorry! This version of Kano OS requires a Raspberry Pi 2 or later.\n"
        "Don't worry. You can get a version optimized for your computer.\n"
        "Head to kano.me/downloads and grab Kano OS v2.1.\n"
    ))
    time.sleep(60)

    # Prevent boot loops during testing by disabling the service. Because of
    # how early during boot this script is executed, the filesystem needs to
    # be temporarily mounted to enable writes.
    if args['--no-detect']:
        run_cmd('sudo mount -o remount,rw /dev/mmcblk0p2 /')
        run_cmd('sudo systemctl disable stop-unsupported-rpi-boot.service')
        run_cmd('sudo mount -o remount,ro /dev/mmcblk0p2 /')

    if not args['--dry-run']:
        sysrq_power_off()

    # Exit cleanly.
    return RC.SUCCESS
