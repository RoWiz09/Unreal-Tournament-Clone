from utils import window

game_window = window.window()

while not game_window.get_window_state():
    game_window.update()