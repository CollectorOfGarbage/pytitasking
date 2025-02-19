import keyboard

keyboard.add_hotkey((91, 29, 72), lambda: print("Hotkey Pressed!"))  # Replace with your function

print("Press your hotkey. Press 'ESC' to exit.")
keyboard.wait('esc')
