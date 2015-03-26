#
# user.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# A collection of functions to manipulate users on the OS.
#

import os
import grp
import pwd
import shutil

from kano.utils import run_cmd_log, run_cmd
from kano.logging import logger


DEFAULT_USER_PASSWORD = "kano"
DEFAULT_USER_GROUPS = "tty,adm,dialout,cdrom,audio,users,sudo,video,games," + \
                      "plugdev,input,kanousers"


class UserError(Exception):
    pass


def user_exists(name):
    try:
        user = pwd.getpwnam(name)
    except KeyError:
        return False

    return user is not None


def group_exists(name):
    try:
        group = grp.getgrnam(name)
    except KeyError:
        return False

    return group.gr_name == name


def get_group_members(name):
    group = grp.getgrnam(name)
    return group.gr_mem


def create_user(username):
    if user_exists(username):
        raise UserError("The user '{}' already exists".format(username))

    home = "/home/{}".format(username)
    home_old = '/home/' + username + '-old'

    if os.path.exists(home):
        msg = ("The home directory for the new user '{}' was there already, " +
               "moving it to {}".format(username, home_old))
        logger.warn(msg)
        shutil.move(home, home_old)

    # The umask force is used to blind the actual /home/username
    # folder from other users
    umask_override = '0077'

    cmd = "useradd -m -K UMASK={} -s /bin/bash {}".format(umask_override,
                                                          username)
    _, _, rv = run_cmd_log(cmd)
    if rv != 0:
        msg = "Unable to create new user, useradd failed."
        logger.error(msg)
        raise UserError(msg)

    cmd = "echo '{}:{}' | chpasswd".format(username, DEFAULT_USER_PASSWORD)
    _, _, rv = run_cmd_log(cmd)
    if rv != 0:
        delete_user(username)
        msg = "Unable to change the new user\'s password, chpasswd failed."
        logger.error(msg)
        raise UserError(msg)

    # Make sure the kanousers group exists
    if not group_exists('kanousers'):
        _, _, rv = run_cmd_log('groupadd kanousers -f')
        if rv != 0:
            msg = 'Unable to create the kanousers group, groupadd failed.'
            raise UserError(msg)

    # Add the new user to all necessary groups
    cmd = "usermod -G '{}' {}".format(DEFAULT_USER_GROUPS, username)
    _, _, rv = run_cmd_log(cmd)


def delete_user(username):
    # kill all process from the user
    run_cmd("killall -KILL -u {}".format(username))

    _, _, rv = run_cmd_log("userdel -r {}".format(username))
    if rv != 0:
        raise UserError("Deleting the '{}' failed.".format(username))


def delete_all_users():
    if group_exists('kanousers'):
        for user in get_group_members('kanousers'):
            delete_user(user)
