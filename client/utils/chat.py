from utils import input_lib as in_lib
from utils.font import Font
from utils import ui

import numpy as np
import glfw

has_chat_open=False
msg = ""
shifting = False
all_msg = []

def handle_input(window):
    global has_chat_open, msg, shifting, all_msg
    if has_chat_open:
        if not in_lib.get_key_pressed(in_lib.keyCodes.KEY_ENTER):
            for key in in_lib.cur_hold:
                if in_lib.get_key_pressed(in_lib.keyCodes.__getattribute__(in_lib.keyCodes, key)):
                    if glfw.get_key_name(in_lib.keyCodes.__getattribute__(in_lib.keyCodes, key), 1):
                        if shifting:
                            msg += glfw.get_key_name(in_lib.keyCodes.__getattribute__(in_lib.keyCodes, key), 1).upper()
                        else:
                            msg += glfw.get_key_name(in_lib.keyCodes.__getattribute__(in_lib.keyCodes, key), 1)

                    elif in_lib.get_key_pressed(in_lib.keyCodes.KEY_LEFT_SHIFT):
                        shifting = True

                    elif in_lib.get_key_pressed(in_lib.keyCodes.KEY_SPACE):
                        msg += " "

        else:
            window.network.send_chat_msg(msg)
            all_msg.append(msg)
            msg = ""
            has_chat_open = False

    elif in_lib.get_key_pressed(in_lib.keyCodes.KEY_T):
        has_chat_open = not has_chat_open

    if shifting and not in_lib.get_key_down(in_lib.keyCodes.KEY_LEFT_SHIFT):
        shifting = False

def render_chat(window):
    window
