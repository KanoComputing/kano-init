#
# reset.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The task of reseting the kit to it's original state.
#


from kano_init.status import Status, StatusError
from kano_init.utils import enable_console_autologin, disable_ldm_autostart, \
    unset_ldm_autologin, restore_factory_settings, reconfigure_autostart_policy
from kano_init.user import delete_all_users


def schedule_reset():
    init_status = Status.get_instance()

    if init_status.stage != Status.DISABLED_STAGE:
        msg = "A different task has been scheduled already. Reboot to " + \
              "finish the task before scheduling another one."
        raise StatusError(msg)

    disable_ldm_autostart()
    unset_ldm_autologin()
    enable_console_autologin('root')

    init_status.stage = Status.RESET_STAGE
    init_status.save()

    print 'kano-init RESET scheduled for the next system reboot'


def do_reset():
    restore_factory_settings()
    delete_all_users()
    reconfigure_autostart_policy()

    status = Status.get_instance()
    status.stage = Status.ADD_USER_STAGE
    status.save()
