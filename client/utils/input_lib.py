import glfw

window = None

held_last_frame = []
cur_hold = []

class keyCodes:
    """
        A class which holds all keycodes.
    """

    KEY_A = glfw.KEY_A
    KEY_B = glfw.KEY_B
    KEY_C = glfw.KEY_C
    KEY_D = glfw.KEY_D
    KEY_E = glfw.KEY_E
    KEY_F = glfw.KEY_F
    KEY_G = glfw.KEY_G
    KEY_H = glfw.KEY_H
    KEY_I = glfw.KEY_I
    KEY_J = glfw.KEY_J
    KEY_K = glfw.KEY_K
    KEY_L = glfw.KEY_L
    KEY_M = glfw.KEY_M
    KEY_N = glfw.KEY_N
    KEY_O = glfw.KEY_O
    KEY_P = glfw.KEY_P
    KEY_Q = glfw.KEY_Q
    KEY_R = glfw.KEY_R
    KEY_S = glfw.KEY_S
    KEY_T = glfw.KEY_T
    KEY_U = glfw.KEY_U
    KEY_V = glfw.KEY_V
    KEY_W = glfw.KEY_W
    KEY_X = glfw.KEY_X
    KEY_Y = glfw.KEY_Y
    KEY_Z = glfw.KEY_Z

    KEY_GRAVE = glfw.KEY_GRAVE_ACCENT

    KEY_1 = glfw.KEY_1
    KEY_2 = glfw.KEY_2
    KEY_3 = glfw.KEY_3
    KEY_4 = glfw.KEY_4
    KEY_5 = glfw.KEY_5
    KEY_6 = glfw.KEY_6
    KEY_7 = glfw.KEY_7
    KEY_8 = glfw.KEY_8
    KEY_9 = glfw.KEY_9
    KEY_0 = glfw.KEY_0

    KEY_MINUS = glfw.KEY_MINUS
    KEY_EQUALS = glfw.KEY_EQUAL

    KEY_LEFT_BRACKET = glfw.KEY_LEFT_BRACKET
    KEY_RIGHT_BRACKET = glfw.KEY_RIGHT_BRACKET
    KEY_BACKSLASH = glfw.KEY_BACKSLASH

    KEY_SEMICOLON = glfw.KEY_SEMICOLON
    KEY_SINGLE_QUOTE = glfw.KEY_APOSTROPHE

    KEY_COMMA = glfw.KEY_COMMA
    KEY_PERIOD = glfw.KEY_PERIOD

    KEY_SLASH = glfw.KEY_SLASH

    KEY_TAB = glfw.KEY_TAB
    KEY_LEFT_SHIFT = glfw.KEY_LEFT_SHIFT
    KEY_RIGHT_SHIFT = glfw.KEY_RIGHT_SHIFT
    
    KEY_LEFT_CONTROL = glfw.KEY_LEFT_CONTROL
    KEY_RIGHT_CONTROL = glfw.KEY_RIGHT_CONTROL

    KEY_LEFT_ALT = glfw.KEY_LEFT_ALT
    KEY_RIGHT_ALT = glfw.KEY_RIGHT_ALT

    KEY_LEFT_ARROW = glfw.KEY_LEFT
    KEY_RIGHT_ARROW = glfw.KEY_RIGHT
    KEY_UP_ARROW = glfw.KEY_UP
    KEY_DOWN_ARROW = glfw.KEY_DOWN

    KEY_SPACE = glfw.KEY_SPACE

    KEY_ENTER = glfw.KEY_ENTER

class mouseButtons:
    """
        A class which holds all mouse buttons.
    """
    LEFT = glfw.MOUSE_BUTTON_LEFT
    RIGHT = glfw.MOUSE_BUTTON_RIGHT
    MIDDLE = glfw.MOUSE_BUTTON_MIDDLE
    MOUSE_4 = glfw.MOUSE_BUTTON_4
    MOUSE_5 = glfw.MOUSE_BUTTON_5
    MOUSE_6 = glfw.MOUSE_BUTTON_6
    MOUSE_7 = glfw.MOUSE_BUTTON_7
    MOUSE_8 = glfw.MOUSE_BUTTON_8

def get_mouse_button_down(mouse_button : mouseButtons):
    global cur_hold
    
    for button in dir(mouseButtons):
        if getattr(mouseButtons, button) == mouse_button and button in cur_hold:
            return True
        
    return False

def get_mouse_button_pressed(mouse_button : mouseButtons):
    global cur_hold, held_last_frame
    
    for button in dir(mouseButtons):
        if getattr(mouseButtons, button) == mouse_button and button in cur_hold and not button in held_last_frame:
            return True
        
    return False

def get_mouse_button_released(mouse_button : mouseButtons):
    global cur_hold, held_last_frame
    
    for button in dir(mouseButtons):
        if getattr(mouseButtons, button) == mouse_button and not button in cur_hold and button in held_last_frame:
            return True
        
    return False

def get_key_down(key : keyCodes):
    global cur_hold
    
    for keycode in dir(keyCodes):
        if getattr(keyCodes, keycode) == key and keycode in cur_hold:
            return True

    return False

def get_key_pressed(key : keyCodes):
    global cur_hold, held_last_frame
    
    for keycode in dir(keyCodes):
        if getattr(keyCodes, keycode) == key and keycode in cur_hold and not keycode in held_last_frame:
            return True

    return False

def get_key_released(key : keyCodes):
    global cur_hold, held_last_frame
    
    for keycode in dir(keyCodes):
        if getattr(keyCodes, keycode) == key and not keycode in cur_hold and keycode in held_last_frame:
            return True

    return False

def handle_inputs(window):
    global held_last_frame, cur_hold

    held_last_frame = cur_hold.copy()
    cur_hold.clear()

    # handle keyboard inputs
    for key in dir(keyCodes):
        if all((not key.startswith("__"), not callable(getattr(keyCodes, key)))):
            if glfw.get_key(window, getattr(keyCodes, key)):
                cur_hold.append(key)

    # handle mouse inputs
    for button in dir(mouseButtons):
        if all((not button.startswith("__"), not callable(getattr(mouseButtons, button)))):
            if glfw.get_mouse_button(window, getattr(mouseButtons, button)):
                cur_hold.append(button)
        