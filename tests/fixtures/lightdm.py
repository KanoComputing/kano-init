#
# lightdm.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Definition of fixtures for LightDM configuration files
#


import os
import pytest


LIGHTDM_CONF_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'lightdm'
)
NO_USER_LIGHTDM_CONF = os.path.join(
    LIGHTDM_CONF_DIR, 'no_user_lightdm.conf'
)
SINGLE_USER_LIGHTDM_CONF = os.path.join(
    LIGHTDM_CONF_DIR, 'single_user_lightdm.conf'
)
MULTI_USER_LIGHTDM_CONF = os.path.join(
    LIGHTDM_CONF_DIR, 'multi_user_lightdm.conf'
)


def load_conf_file(conf_path):
    '''
    Helper function to read the supplied config file path.
    '''

    with open(conf_path, 'r') as conf_f:
        conf = conf_f.read()

    return conf


@pytest.fixture(scope='function')
def no_user_lightdm_conf():
    '''
    Provides the LightDM configuration file expected when no users exist.
    '''

    return {
        'users': [],
        'conf': load_conf_file(NO_USER_LIGHTDM_CONF)
    }


@pytest.fixture(scope='function')
def single_user_lightdm_conf():
    '''
    Provides the LightDM configuration file expected when one user (named
    "kano") exists.
    '''

    return {
        'users': ['kano'],
        'conf': load_conf_file(SINGLE_USER_LIGHTDM_CONF)
    }


@pytest.fixture(scope='function')
def multi_user_lightdm_conf():
    '''
    Provides the LightDM configuration file expected when 3 users (named "kano",
    "kanotest1", "someotheruser") exist.
    '''

    return {
        'users': ['kano', 'kanotest1', 'someotheruser'],
        'conf': load_conf_file(MULTI_USER_LIGHTDM_CONF)
    }


LIGHTDM_CONFS = (
    no_user_lightdm_conf(),
    single_user_lightdm_conf(),
    multi_user_lightdm_conf(),
)


@pytest.fixture(scope='function', params=LIGHTDM_CONFS)
def lightdm_conf(request):
    '''
    Provides a selection of LightDM configuration files.
    '''

    return request.param


@pytest.fixture(scope='function', params=LIGHTDM_CONFS)
def lightdm_conf_file(request, fs):
    '''
    Provides a selection of LightDM configuration files, provided directly via a
    pyfakefs file.
    '''

    import kano_init.utils

    conf = request.param['conf']
    conf_file = fs.CreateFile(
        kano_init.utils.LIGHTDM_CONF_FILE,
        contents=conf
    )

    return conf_file


@pytest.fixture(scope='function')
def mock_console_autologin(monkeypatch):
    '''
    Override the `kano_init.utils.enable_console_autologin()` and
    `kano_init.utils.disable_console_autologin()` functions with ones which do
    nothing.
    '''

    import kano_init.utils

    monkeypatch.setattr(
        kano_init.utils, 'enable_console_autologin',
        lambda x: True
    )
    monkeypatch.setattr(
        kano_init.utils, 'disable_console_autologin',
        lambda: True
    )
    yield


@pytest.fixture(scope='function')
def mock_ldm_autostart(monkeypatch):
    '''
    Override the `kano_init.utils.enable_ldm_autostart()` and
    `kano_init.utils.disable_ldm_autostart()` functions with ones which do
    nothing.
    '''

    import kano_init.utils

    monkeypatch.setattr(
        kano_init.utils, 'enable_ldm_autostart',
        lambda: True
    )
    monkeypatch.setattr(
        kano_init.utils, 'disable_ldm_autostart',
        lambda: True
    )
    yield



@pytest.fixture(scope='function')
def mock_get_group_members(monkeypatch):
    '''
    Provides a method to override the `kano_init.utils.mock_get_group_members()`
    function with the list of users provided.

    E.g.

    def test_example(mock_get_group_members):
        mock_get_group_members(['some', 'list', 'of', 'users'])
    '''

    import kano_init.utils

    def patch(users):
        monkeypatch.setattr(
            kano_init.utils, 'get_group_members',
            lambda x: users
        )

    return patch
