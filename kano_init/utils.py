#
# utils.py
#
# Copyright (C) 2015-2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# A collection of utilities for the initflow.
#


import os
import json
import shutil

import pwd
import grp

from kano.utils.shell import run_cmd
from kano.utils.file_operations import ensure_dir, sed

from kano_init.paths import INIT_CONF_PATH, DEFAULT_LIGHTDM_CONF_FILE
from kano_init.user import get_group_members
from kano_init.status import Status


LIGHTDM_CONF_FILE = '/etc/lightdm/lightdm.conf'


def enable_console_autologin(username, restart=False):
    '''
    Sets the system to automatically login username on tty1
    at boot time, or when you close the console session.
    '''

    #
    # Change systemd symlink that points to what needs to happen on tty1
    # https://wiki.archlinux.org/index.php/Systemd_FAQ#How_do_I_change_the_default_number_of_gettys.3F
    #
    systemd_tty1_linkfile = '/etc/systemd/system/getty.target.wants/getty@tty1.service'
    kano_init_tty1_kanoautologin = '/usr/share/kano-init/systemd_ttys/kanoautologin@.service'
    kano_init_tty1_kanoinit = '/usr/share/kano-init/systemd_ttys/kanoinit@.service'
    if os.path.isfile(systemd_tty1_linkfile):
        os.unlink(systemd_tty1_linkfile)

    if username == 'root':
        os.symlink(kano_init_tty1_kanoinit, systemd_tty1_linkfile)
    else:
        sed('^ExecStart.*', "ExecStart=/bin/su - {}".format(username), kano_init_tty1_kanoautologin)
        os.symlink(kano_init_tty1_kanoautologin, systemd_tty1_linkfile)

    if restart:
        # replace the tty process immediately, otherwise on next boot
        run_cmd('systemctl restart getty@tty1.service')


def disable_console_autologin(restart=False):
    '''
    Disable automatic login on tty1, default getty login prompt will be provided.
    '''

    #
    # Change systemd symlink that points to what needs to happen on tty1
    # https://wiki.archlinux.org/index.php/Systemd_FAQ#How_do_I_change_the_default_number_of_gettys.3F
    #
    systemd_tty1_linkfile = '/etc/systemd/system/getty.target.wants/getty@tty1.service'
    systemd_tty1_getty = '/lib/systemd/system/getty@.service'

    if os.path.isfile(systemd_tty1_linkfile):
        os.unlink(systemd_tty1_linkfile)

    os.symlink(systemd_tty1_getty, systemd_tty1_linkfile)

    if restart:
        run_cmd('systemctl restart getty@tty1.service')


def set_ldm_autologin(username):
    '''
    Tell lightdm to skip the greeter, login username, and go directly to the desktop.
    '''
    sed('^#?(autologin-user)=.*$', 'autologin-user={}'.format(username), LIGHTDM_CONF_FILE)

    # Make sure the autologin timeout is set to 0
    sed('^#?(autologin-user-timeout)=.*$', '\\1=0', LIGHTDM_CONF_FILE)


def unset_ldm_autologin():
    '''
    Disable lightdm automatic login, the greeter should provide a login window
    '''
    sed('^autologin-user=.*$', '#autologin-user=none', LIGHTDM_CONF_FILE)

    # Comment out the autologin-user-timeout option
    sed('^#?(autologin-user-timeout=.*)$', '#\\1', LIGHTDM_CONF_FILE)


def enable_ldm_autostart():
    '''
    Set the system to graphical mode - start the default X server and go to Desktop
    '''
    run_cmd('systemctl set-default graphical.target')


def disable_ldm_autostart():
    '''
    Set the system to multi user mode - the X server will not be started,
    and the Overture onboarding will take control, through the systemd service.
    '''
    run_cmd('systemctl set-default multi-user.target')


def start_lightdm():
    '''
    Starts the X server immediately, it is safe to call while overture is running
    '''
    run_cmd('systemctl start lightdm')


def start_dashboard_services(username):
    '''
    Starts the Dashboard app and related user services on top of the XServer,
    Using su to impersonate them as the specified "username".
    '''
    run_cmd('su - "{}" -c "systemctl --user start kano-dashboard.service"'.format(username))
    run_cmd('su - "{}" -c "systemctl --user restart kano-common.target"'.format(username))


def set_dashboard_onboarding(username, run_it=True):
    '''
    FIXME: This onboarding stage is to be superseded by Overture
    Tells the Dashboard supervisor whether the Onboarding needs to take place
    '''
    onboarding_file=os.path.join('/home/{}'.format(username),
                                 '.dashboard-onboarding-done')

    if run_it:
        # Remove the mark file so the supervisor will go through Onboarding
        if os.path.isfile(onboarding_file):
            os.unlink(onboarding_file)
    else:
        # Create the mark file so Dashboard Supervisor will skip Onboarding
        with open(onboarding_file, 'w'):
            os.utime(onboarding_file, None)

        # Make sure file has correct ownership
        uid = pwd.getpwnam(username).pw_uid
        gid = grp.getgrnam(username).gr_gid
        os.chown(onboarding_file, uid, gid)


def reconfigure_autostart_policy():
    '''
    Set the system boot flow depending on which users are available on the system.
    With no kano users, set things ready to start the Onboarding on boot.
    With one kano users, set the system to go directly to the Dashboard.
    With more than once kano user, set the system to go to the login Greeter.
    '''
    kanousers = get_group_members('kanousers')
    if len(kanousers) == 0:
        enable_console_autologin('root')
        unset_ldm_autologin()
        disable_ldm_autostart()
    elif len(kanousers) == 1:
        enable_console_autologin(kanousers[0])
        set_ldm_autologin(kanousers[0])
        enable_ldm_autostart()
    else:
        disable_console_autologin()
        unset_ldm_autologin()
        enable_ldm_autostart()


def ensure_lightdm_conf():
    '''
    If the LightDM config file is missing then the undesirable LXDE login screen
    appears rather than our greeter. Ensure that the file exists and create the
    correct one if it doesn't
    '''

    if os.path.exists(LIGHTDM_CONF_FILE):
        return

    ensure_dir(os.path.dirname(LIGHTDM_CONF_FILE))
    shutil.copy(DEFAULT_LIGHTDM_CONF_FILE, LIGHTDM_CONF_FILE)
    reconfigure_autostart_policy()


def restore_factory_settings():
    # FIXME: These imports are local because importing kano_settings.config_file
    # has side effects that break peldins build
    from kano_settings.default import set_default_config

    # remove the wifi cache, effectively avoiding a wireless connection on boot
    try:
        os.remove('/etc/kwifiprompt-cache.conf')
    except Exception:
        pass

    set_default_config()


def is_any_task_scheduled():
    '''
    Returns True if there is an uncompleted kano-init task
    '''
    status = Status.get_instance()
    return status.stage != Status.DISABLED_STAGE


def load_init_conf():
    """
    Load the init configuration from the boot partition.

    :return: The config in a dictionary.
    :rtype: dict
    """
    flow_params = {}
    if os.path.exists(INIT_CONF_PATH):
        with open(INIT_CONF_PATH, 'r') as init_conf:
            init_conf_data = json.load(init_conf)

            # The old convention with an underscore
            if 'kano_init' in init_conf_data:
                flow_params = init_conf_data['kano_init']

            # A hyphen with a bigger priority
            if 'kano-init' in init_conf_data:
                flow_params = init_conf_data['kano-init']

    return flow_params
