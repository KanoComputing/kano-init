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

from kano.utils import sed, run_cmd
from kano_settings.system.keyboard_config import set_keyboard
from kano_settings.config_file import file_replace
from kano_settings.boot_config import set_config_value, set_config_comment
from kano_settings.system.overclock import set_default_overclock_values
from kano.utils import is_model_2_b

from kano_init.paths import INIT_CONF_PATH
from kano_init.user import get_group_members
from kano_init.status import Status


def enable_console_autologin(username):
    sed('^(1:2345:respawn:/sbin/a?getty).+',
        "\\1 -n -o\'-f {}\' 38400 tty1".format(username),
        '/etc/inittab')
    run_cmd('init q')


def disable_console_autologin():
    sed('^(1:2345:respawn:/sbin/a?getty).+', '\\1 38400 tty1', '/etc/inittab')
    run_cmd('init q')


def set_ldm_autologin(username):
    ldm_conf_util = '/usr/lib/arm-linux-gnueabihf/lightdm/lightdm-set-defaults'
    run_cmd("{} --autologin {}".format(ldm_conf_util, username))


def unset_ldm_autologin():
    sed('^autologin-user=.*$', '', '/etc/lightdm/lightdm.conf')


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
    # removing wifi cache
    try:
        os.remove('/etc/kwifiprompt-cache.conf')
    except Exception:
        pass

    # set the keyboard to default
    set_keyboard('en_US', 'generic')

    # setting the audio to analogue
    amixer_from = "amixer -c 0 cset numid=3 [0-9]"
    amixer_to = "amixer -c 0 cset numid=3 1"

    file_replace("/etc/rc.audio", amixer_from, amixer_to)
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
