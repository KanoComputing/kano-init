#
# utils.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# A collection of utilities for the initflow.
#

import os
import json

from kano.utils import sed, run_cmd, is_systemd

from kano_init.paths import INIT_CONF_PATH
from kano_init.user import get_group_members
from kano_init.status import Status
from kano_settings.system.audio import set_to_HDMI


def enable_console_autologin(username, restart=False):
    '''
    Sets the system to automatically login username on tty1
    at boot time, or when you close the console session.
    '''
    if is_systemd():
        #
        # Change systemd symlink that says what needs to happen on tty1
        # https://wiki.archlinux.org/index.php/Systemd_FAQ#How_do_I_change_the_default_number_of_gettys.3F
        #
        systemd_tty1_linkfile='/etc/systemd/system/getty.target.wants/getty@tty1.service'
        kano_init_tty1_kanoautologin='/usr/share/kano-init/systemd_ttys/kanoautologin@.service'
        kano_init_tty1_kanoinit='/usr/share/kano-init/systemd_ttys/kanoinit@.service'
        
        if os.path.isfile(systemd_tty1_linkfile):
            os.unlink(systemd_tty1_linkfile)

        if username=='root':
            os.symlink(kano_init_tty1_kanoinit, systemd_tty1_linkfile)            
        else:
            sed('^ExecStart.*', "ExecStart=/bin/su - {}".format(username), kano_init_tty1_kanoautologin)
            os.symlink(kano_init_tty1_kanoautologin, systemd_tty1_linkfile)

        if restart:
            # replace the tty process inmediately, otherwise on next boot
            run_cmd('systemctl restart getty@tty1.service')
    else:
        sed('^(1:2345:respawn:/sbin/a?getty).+',
            "\\1 -n -o\'-f {}\' 38400 tty1".format(username),
            '/etc/inittab')
        run_cmd('init q')

def disable_console_autologin(restart=False):
    '''
    Disable automatic login on tty1, default getty login prompt will be provided.
    '''
    if is_systemd():
        #
        # Change systemd symlink that says what needs to happen on tty1
        # https://wiki.archlinux.org/index.php/Systemd_FAQ#How_do_I_change_the_default_number_of_gettys.3F
        #
        systemd_tty1_linkfile='/etc/systemd/system/getty.target.wants/getty@tty1.service'
        systemd_tty1_getty='/lib/systemd/system/getty@.service'

        if os.path.isfile(systemd_tty1_linkfile):
            os.unlink(systemd_tty1_linkfile)

        os.symlink(systemd_tty1_getty, systemd_tty1_linkfile)

        if restart:
            run_cmd('systemctl start getty@tty1.service')
    else:
        sed('^(1:2345:respawn:/sbin/a?getty).+', '\\1 38400 tty1', '/etc/inittab')
        run_cmd('init q')


def set_ldm_autologin(username):
    ldm_conf_util = '/usr/lib/arm-linux-gnueabihf/lightdm/lightdm-set-defaults'
    run_cmd("{} --autologin {}".format(ldm_conf_util, username))

    # Make sure the autologin timeout is set to 0
    sed('^#?(autologin-user-timeout)=.*$', '\\1=0', '/etc/lightdm/lightdm.conf')


def unset_ldm_autologin():
    sed('^autologin-user=.*$', '', '/etc/lightdm/lightdm.conf')
    
    # Comment out the autologin-user-timeout option
    sed('^#?(autologin-user-timeout=.*)$', '#\\1', '/etc/lightdm/lightdm.conf')


def enable_ldm_autostart():
    run_cmd('update-rc.d lightdm enable 2')


def disable_ldm_autostart():
    run_cmd('update-rc.d lightdm disable 2')


def reconfigure_autostart_policy():
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


def restore_factory_settings():
    # FIXME: These imports are local because importing kano_settings.config_file
    # has side effects that break peldins build
    from kano_settings.system.keyboard_config import set_keyboard
    from kano_settings.config_file import file_replace
    from kano_settings.boot_config import set_config_value, set_config_comment
    from kano_settings.system.overclock import set_default_overclock_values
    from kano.utils import is_model_2_b
    
    # removing wifi cache
    try:
        os.remove('/etc/kwifiprompt-cache.conf')
    except Exception:
        pass

    # set the keyboard to default
    set_keyboard('en_US', 'generic')

    # setting the audio to analogue
    set_to_HDMI(False)
    
    set_config_value('hdmi_ignore_edid_audio', 1)
    set_config_value('hdmi_drive', None)

    # resetting HDMI settings
    set_config_value('disable_overscan', 1)
    set_config_value('overscan_left', 0)
    set_config_value('overscan_right', 0)
    set_config_value('overscan_top', 0)
    set_config_value('overscan_bottom', 0)
    set_config_value('hdmi_pixel_encoding', 2)
    set_config_value('hdmi_group', None)
    set_config_value('hdmi_mode', None)
    set_config_comment('kano_screen_used', 'xxx')

    # resetting overclocking settings
    set_default_overclock_values(is_model_2_b())


def is_any_task_scheduled():
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
