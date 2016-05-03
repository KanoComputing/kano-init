#
# flow.py
#
# Copyright (C) 2015, 2016 Kano Computing Ltd.
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

from kano.colours import decorate_with_preset
from kano.utils import run_cmd, ensure_dir, delete_dir

from kano_init.paths import SUBSHELLRC_PATH
from kano_init.terminal import typewriter_echo, clear_screen, user_input, \
    write_flush, LEFT_PADDING, set_overscan, reset_overscan
from kano_init.status import Status
from kano_init.ascii_art.matrix import matrix
from kano_init.ascii_art.matrix_binary import matrix_binary
from kano_init.ascii_art.rabbit import rabbit
from kano_init.ascii_art.binary import binary
from kano_init.user import user_exists, create_user, make_username_unique
from kano_init.utils import reconfigure_autostart_policy, set_ldm_autologin, \
    set_dashboard_onboarding

from kano_settings.system.advanced import set_hostname


def do_username_stage(flow_params):
    """
    """

    if flow_params.get('skip'):
        # Skip the interactive flow and create the user automatically
        if 'user' in flow_params:
            username = flow_params['user']
        else:
            username = 'kano'

        username = make_username_unique(username)
    else:
        try:
            reset_overscan()
            matrix(2, True, set_overscan)
        except:
            pass
        clear_screen()

        typewriter_echo('Hello!', trailing_linebreaks=2)
        typewriter_echo('Thanks for bringing me to life. Now, let\'s see what we can do.',
                        sleep=0.5, trailing_linebreaks=2)
        typewriter_echo('What is your name?', trailing_linebreaks=2)

        username = _get_username()

    create_user(username)

    # set the hostname to the same as the username
    set_hostname(username)

    # Next up is the white rabit stage
    init_status = Status.get_instance()
    init_status.stage = Status.LIGHTUP_STAGE
    init_status.username = username
    init_status.save()


def do_lightup_stage(flow_params):
    init_status = Status.get_instance()

    if not flow_params.get('skip', False):
        clear_screen()

        msg = "Nice to meet you {}.".format(init_status.username)
        typewriter_echo(msg, trailing_linebreaks=2)

        msg = "Did you know your new computer\'s brain is made of millions"
        typewriter_echo(msg, trailing_linebreaks=1)

        msg = "of electric switches?"
        typewriter_echo(msg, trailing_linebreaks=2)

        msg = "Press [ENTER] to see what the switches do."
        typewriter_echo(msg, trailing_linebreaks=2)

        # Wait for user input
        raw_input(LEFT_PADDING * ' ')

    init_status.stage = Status.SWITCH_STAGE
    init_status.save()


def do_switch_stage(flow_params):
    init_status = Status.get_instance()

    if not flow_params.get('skip', False):
        clear_screen()

        try:
            binary(init_status.username)
        except EnvironmentError:
            pass

    init_status.stage = Status.LETTERS_STAGE
    init_status.save()


def do_letters_stage(flow_params):
    init_status = Status.get_instance()

    if not flow_params.get('skip', False):

        # Initially we will jump to this step on completion
        init_status.stage = Status.WHITE_RABBIT_STAGE

        clear_screen()

        msg = "Words, music and pictures all get stored as binary code."
        typewriter_echo(msg, trailing_linebreaks=2)

        msg = "And so does your computer\'s secret password:"
        typewriter_echo(msg, trailing_linebreaks=2)

        msg = "01101011 01100001 01101110 01101111"
        typewriter_echo(msg, trailing_linebreaks=1)
        msg = "   k        a        n        o    "
        typewriter_echo(msg, trailing_linebreaks=2)

        msg = "Type the secret password in human letters:"
        typewriter_echo(msg, trailing_linebreaks=2)

        attempts = 0
        while True:
            # Wait for user input
            terminal = LEFT_PADDING * ' '
            terminal = terminal + "{}@kano ~ $ ".format(init_status.username)
            password = raw_input(terminal).lower()
            attempts += 1
            if password == "kano" or \
               password == "01101011 01100001 01101110 01101111" or \
               password == "01101011011000010110111001101111":
                break

            elif password == "class":

                # Class mode: Take the teacher directly to the Dashboard

                # Disable the onboarding
                set_dashboard_onboarding(init_status.username, run_it=False)

                # Take kano-init to the final step
                init_status.stage = Status.FINAL_STAGE

                msg = "Ok! Taking you to the Dashboard..."
                typewriter_echo(msg, sleep=0.5, trailing_linebreaks=1)

                break

            else:
                if attempts < 3:
                    msg = "Not the correct password, keep trying!"
                    typewriter_echo(msg, trailing_linebreaks=2)
                else:
                    msg = "The secret password is kano"
                    typewriter_echo(msg, trailing_linebreaks=2)
                    raw_input("Press [ENTER] to keep exploring.")
                    break

    init_status.save()


def do_white_rabbit_stage(flow_params):
    init_status = Status.get_instance()

    if not flow_params.get('skip', False):
        clear_screen()
        try:
            rabbit(1, 'left-to-right')
        except:
            pass
        clear_screen()

        msg = "Woah."
        typewriter_echo(msg, trailing_linebreaks=2)

        msg = "{}, did you see that?".format(init_status.username)
        typewriter_echo(msg, trailing_linebreaks=2)

        command = decorate_with_preset('cd rabbithole', 'code')
        typewriter_echo("Type {} to follow the white rabbit.".format(command),
                        trailing_linebreaks=2)

        # TODO: open shell
        rabbithole = "/home/{}/rabbithole".format(init_status.username)
        ensure_dir(rabbithole)
        cmd = "sudo -u {} -H bash --init-file {}".format(init_status.username,
                                                         SUBSHELLRC_PATH)
        os.system(cmd)
        delete_dir(rabbithole)

        reset_overscan()
        matrix_binary(1, False)
        set_overscan()

        clear_screen()

    init_status.stage = Status.LOVE_STAGE
    init_status.save()


def do_love_stage(flow_params):
    init_status = Status.get_instance()

    if not flow_params.get('skip', False):
        clear_screen()
        # kanoOverworld needs to run as the user
        # to access the savefile correctly.
        cmd = 'su {} -c "/usr/bin/love /usr/bin/kanoOverworld.love --load" >>/var/log/kanoOverworld.log 2>&1'.format(init_status.username)

        reset_overscan()
        os.system(cmd)
        set_overscan()

    init_status.stage = Status.FINAL_STAGE
    init_status.save()


def do_final_stage(flow_params):
    init_status = Status.get_instance()

    clear_screen()

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
        username = re.sub('\s+', '', username)
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
