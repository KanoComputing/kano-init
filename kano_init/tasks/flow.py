#
# flow.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

"""
    This file contains the three stages that constitute the initialisation
    procedure when creating a user during boot via kano-init.

    Each of the do_* functions represents a stage from the flow. It will
    do its task and schedule the subsequent stage.
"""

import re
import os
import time

from kano.colours import decorate_with_preset
from kano.utils import run_cmd, ensure_dir, delete_dir

from kano_init.paths import SUBSHELLRC_PATH
from kano_init.terminal import typewriter_echo, clear_screen, user_input, \
    write_flush
from kano_init.status import Status
from kano_init.ascii_art.matrix import matrix
from kano_init.ascii_art.rabbit import rabbit
from kano_init.ascii_art.bomb import bomb
from kano_init.user import user_exists, create_user, make_username_unique
from kano_init.utils import reconfigure_autostart_policy, set_ldm_autologin, \
    disable_ldm_autostart, enable_ldm_autostart


def do_username_stage(flow_params):
    """
    """

    if 'skip' in flow_params and flow_params['skip']:
        # Skip the interactive flow and create the user automatically
        if 'user' in flow_params:
            username = flow_params['user']
        else:
            username = 'kano'

        username = make_username_unique(username)
    else:
        matrix(2, True)
        clear_screen()

        typewriter_echo('Hello!', trailing_linebreaks=2)
        typewriter_echo('I\'m KANO. Thanks for bringing me to life.',
                        sleep=0.5, trailing_linebreaks=2)
        typewriter_echo('What should I call you?', trailing_linebreaks=2)

        username = _get_username()

    create_user(username)

    # Next up is the white rabit stage
    init_status = Status.get_instance()
    init_status.stage = Status.WHITE_RABBIT_STAGE
    init_status.username = username
    init_status.save()


def do_white_rabbit_stage(flow_params):
    init_status = Status.get_instance()

    if not 'skip' in flow_params or not flow_params['skip']:
        clear_screen()
        rabbit(1, 'left-to-right')
        clear_screen()

        msg = "{}, follow the white rabbit ...".format(init_status.username)
        typewriter_echo(msg, trailing_linebreaks=2)

        typewriter_echo('He\'s hiding in my memory. Can you find him?',
                        trailing_linebreaks=2)

        command = decorate_with_preset('cd rabbithole', 'code')
        typewriter_echo("Type {}".format(command), trailing_linebreaks=2)

        # TODO: open shell
        rabbithole = "/home/{}/rabbithole".format(init_status.username)
        ensure_dir(rabbithole)
        cmd = "sudo -u {} -H bash --init-file {}".format(init_status.username,
                                                         SUBSHELLRC_PATH)
        os.system(cmd)
        delete_dir(rabbithole)

        matrix(2, False)
        clear_screen()
        rabbit(1, 'right-to-left')
        
        clear_screen()
        msg = "{}, it's a trap!".format(init_status.username)
        typewriter_echo(msg)
        time.sleep(2)

    init_status.stage = Status.STARTX_STAGE
    init_status.save()


def do_startx_stage(flow_params):
    init_status = Status.get_instance()

    if not 'skip' in flow_params or not flow_params['skip']:
        clear_screen(False)
        while True:
            if bomb(init_status.username) == 0:
                clear_screen(False)
                break

            clear_screen(True)
            time.sleep(1)
            typewriter_echo('Try again!', sleep=2)

    reconfigure_autostart_policy()

    # Force autologin for this user until he goes through the graphic
    # init flow. At the end of it, kano-uixinit should call kano-init
    # to finalise the process and switch the kit to multiuser.
    set_ldm_autologin(init_status.username)

    init_status.stage = Status.UI_INIT_STAGE
    init_status.save()

    run_cmd('service lightdm start')


def _get_username():
    while True:
        username = user_input('Your name: ').strip()
        write_flush('\n')

        if len(username) == 0:
            typewriter_echo('Type a cool name.', trailing_linebreaks=2)
        elif not re.match("^[a-zA-Z0-9]+$", username):
            typewriter_echo('Just one word, letters or numbers! Try again.',
                trailing_linebreaks=2)
        elif user_exists(username):
            typewriter_echo('This one is already taken! Try again.',
                trailing_linebreaks=2)
        elif len(username) > 25:
            msg = "This one is too long by {} characters! Try again.".format(
                len(username) - 25
            )
            typewriter_echo(msg, trailing_linebreaks=2)
        else:
            return username
