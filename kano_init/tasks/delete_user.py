#
# delete_user.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The task of removing a user at boot.
#


from kano.logging import logger

from kano_init.status import Status, StatusError
from kano_init.utils import enable_console_autologin, disable_ldm_autostart, \
    unset_ldm_autologin, reconfigure_autostart_policy
from kano_init.user import delete_user, user_exists


def schedule_delete_user(name):
    status = Status.get_instance()

    if status.stage != Status.DISABLED_STAGE:
        msg = "A different task has been scheduled already. Reboot to " + \
              "finish the task before scheduling another one."
        raise StatusError(msg)

    status.stage = Status.DELETE_USER_STAGE
    status.username = name
    status.save()

    disable_ldm_autostart()
    unset_ldm_autologin()
    enable_console_autologin('root')

    print "The '{}' user will be deleted on the next reboot.".format(name)


def do_delete_user():
    status = Status.get_instance()

    user = status.username
    if user_exists(user):
        delete_user(user)
    else:
        logger.warn("Attempt to delete nonexisting user ({})".format(user))

    reconfigure_autostart_policy()

    status.username = None
    status.stage = Status.DISABLED_STAGE
    status.save()
