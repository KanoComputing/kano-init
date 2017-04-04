#
# reset.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The task of reseting the kit to it's original state.
#

import os

from kano_init.status import Status, StatusError
from kano_init.utils import disable_ldm_autostart, \
    unset_ldm_autologin, restore_factory_settings, reconfigure_autostart_policy
from kano_init.user import delete_all_users


def schedule_reset():
    init_status = Status.get_instance()

    if init_status.stage != Status.DISABLED_STAGE:
        msg = _("A different task has been scheduled already. Reboot to"
                " finish the task before scheduling another one.")
        raise StatusError(msg)

    disable_ldm_autostart()
    unset_ldm_autologin()

    init_status.stage = Status.RESET_STAGE
    init_status.save()

    print _("kano-init RESET scheduled for the next system reboot").encode('utf8')


def do_reset(flow_param):
    restore_factory_settings()
    delete_all_users()
    reconfigure_autostart_policy()

    status = Status.get_instance()
    status.stage = Status.ADD_USER_STAGE
    status.save()

    # Reboot before initiating the next stage to make sure the
    # settings are correct.
    os.system('kano-checked-reboot kano-init systemctl reboot')
