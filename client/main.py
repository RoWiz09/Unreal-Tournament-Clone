from utils import window

game_window = window.window((600, 500))

while not game_window.get_window_state():
    game_window.update()