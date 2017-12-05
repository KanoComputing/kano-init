#
# test_login.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for login-setting functions (mainly from `kano_init.utils`)
#


import os


def test_reconfigure_autostart_policy(
        lightdm_conf_file, lightdm_conf, mock_console_autologin,
        mock_ldm_autostart, mock_get_group_members
    ):
    '''
    Checks the `kano_init.utils.reconfigure_autostart_policy()` function for
    a selection of base configuration states, changing to different user
    account states.

    Note, we are mocking the `enable/disable_console_autologin()` and
    `enable/disable_ldm_autostart()` functions so the test isn't complete.
    '''

    import kano_init.utils

    mock_get_group_members(lightdm_conf['users'])

    # Run the function to test
    kano_init.utils.reconfigure_autostart_policy()

    with open(kano_init.utils.LIGHTDM_CONF_FILE, 'r') as conf_f:
        assert conf_f.read() == lightdm_conf['conf']



def test_ensure_lightdm_conf_no_conf_dir(
        fs, lightdm_conf, mock_console_autologin,
        mock_ldm_autostart, mock_get_group_members
    ):
    '''
    Checks the `kano_init.utils.ensure_lightdm_conf()` function in the case
    where the `/etc/lightdm/` directory exists.
    '''

    import kano_init.utils
    import kano_init.paths

    # Expose the default configuration file from the real FS
    fs.add_real_file(kano_init.paths.DEFAULT_LIGHTDM_CONF_FILE)

    mock_get_group_members(lightdm_conf['users'])

    # Run the function to test
    kano_init.utils.ensure_lightdm_conf()

    # Checks
    with open(kano_init.utils.LIGHTDM_CONF_FILE, 'r') as conf_f:
        assert conf_f.read() == lightdm_conf['conf']



def test_ensure_lightdm_conf_no_conf(
        fs, lightdm_conf, mock_console_autologin,
        mock_ldm_autostart, mock_get_group_members
    ):
    '''
    Checks the `kano_init.utils.ensure_lightdm_conf()` function in the case
    where no `/etc/lightdm/lightdm.conf` file exists.
    '''

    import kano_init.utils
    import kano_init.paths


    fs.CreateDirectory(
        os.path.dirname(kano_init.utils.LIGHTDM_CONF_FILE)
    )

    # Expose the default configuration file from the real FS
    fs.add_real_file(kano_init.paths.DEFAULT_LIGHTDM_CONF_FILE)

    mock_get_group_members(lightdm_conf['users'])

    # Run the function to test
    kano_init.utils.ensure_lightdm_conf()

    # Checks
    with open(kano_init.utils.LIGHTDM_CONF_FILE, 'r') as conf_f:
        assert conf_f.read() == lightdm_conf['conf']



def test_ensure_lightdm_conf_with_conf(
        lightdm_conf_file, lightdm_conf, mock_console_autologin,
        mock_ldm_autostart, mock_get_group_members
    ):
    '''
    Checks the `kano_init.utils.ensure_lightdm_conf()` function in the case
    where a variety base `/etc/lightdm/lightdm.conf` configurations exist.
    '''

    import kano_init.utils

    mock_get_group_members(lightdm_conf['users'])

    # Run the function to test
    kano_init.utils.ensure_lightdm_conf()

    # Checks
    with open(kano_init.utils.LIGHTDM_CONF_FILE, 'r') as conf_f:
        assert conf_f.read() == lightdm_conf_file.contents
