#
# flow.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The initialisation procedure for the user
#

import re
import os
import pwd
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


class FlowError(Exception):
    pass


def flow(stage_name=None):
    if not stage_name:
        print str(Status.stages)
        stage_name = Status.stages[0]

    try:
        first_stage = Status.stages.index(stage_name)
    except ValueError:
        raise FlowError("Stage '{}' doesn't exist.".format(stage_name))

    # Run all the stages left in the sequence
    for stage in Status.stages[first_stage:]:
        run_stage(stage)


def run_stage(stage_name):
    if stage_name == Status.USERNAME_STAGE:
        run_username_stage()
    elif stage_name == Status.WHITE_RABBIT_STAGE:
        white_rabbit_stage()
    elif stage_name == Status.STARTX_STAGE:
        startx_stage()
    else:
        msg = "Stage handler for '{}' doesn't exist".format(stage_name)
        raise FlowError(msg)


def run_username_stage():
    init_status = Status.get_instance()
    init_status.stage = Status.USERNAME_STAGE
    init_status.save()

    matrix(2, True)

    clear_screen()
    typewriter_echo('Hello!', trailing_linebreaks=2)
    typewriter_echo('I\'m KANO. Thanks for bringing me to life.',
                    sleep=0.5, trailing_linebreaks=2)
    typewriter_echo('What should I call you?', trailing_linebreaks=2)

    username = _get_username()

    # TODO: Create the user

    init_status.username = username
    init_status.save()


def white_rabbit_stage():
    init_status = Status.get_instance()
    init_status.stage = Status.WHITE_RABBIT_STAGE
    init_status.save()

    clear_screen()

    rabbit(1, 'left-to-right')

    msg = "{}, follow the white rabbit ...".format(init_status.username)
    typewriter_echo(msg, trailing_linebreaks=2)

    typewriter_echo('He\'s hiding in my memory. Can you find him?',
                    trailing_linebreaks=2)

    command = decorate_with_preset('cd rabbithole', 'code')
    typewriter_echo("Type {}".format(command), trailing_linebreaks=2)

    # TODO: open shell
    rabbithole = "/home/{}/rabbithole".format(init_status.username)
    ensure_dir(rabbithole)
    cmd = "sudo -u {} -H bash --init-file {}".format(
        init_status.username,
        SUBSHELLRC_PATH
    )
    run_cmd(cmd)
    delete_dir(rabbithole)

    matrix(2, False)

def startx_stage():
    init_status = Status.get_instance()
    #init_status.stage = Status.WHITE_RABBIT_STAGE
    #init_status.save()

    while True:
        clear_screen()

        if bomb(init_status.username) == 0:
            break

        time.sleep(1)
        typewriter_echo('Try again!', sleep=2)

    #run_cmd('service lightdm start')


def _get_username():
    while True:
        username = user_input('Your name: ').strip()
        write_flush('\n')

        if len(username) == 0:
            typewriter_echo('Type a cool name.', trailing_linebreaks=2)
        elif not re.match("^[a-zA-Z0-9]+$", username):
            typewriter_echo('Just one word, letters or numbers! Try again.',
                trailing_linebreaks=2)
        elif username_taken(username):
            typewriter_echo('This one is already taken! Try again.',
                trailing_linebreaks=2)
        elif len(username) > 25:
            msg = "This one is too long by {} characters! Try again.".format(
                len(username) - 25
            )
            typewriter_echo(msg, trailing_linebreaks=2)
        else:
            return username


def username_taken(name):
    try:
        user = pwd.getpwnam(name)
    except KeyError:
        return False

    return user is not None

