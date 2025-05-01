from client import window
    
game_window = window.window((224, 126))

while not game_window.get_window_state():
    game_window.update()

quit()