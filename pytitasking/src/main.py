# FILE: /pytitasking/pytitasking/src/main.py

import tkinter as tk
import threading
import keyboard
from tray_icon import setup_tray_icon
from utils import get_windows, fibonacci_layout, vertical_layout

def launch_app(layout_mode):
    root = tk.Tk()
    app = WindowSelectorApp(root, layout_mode)
    root.mainloop()

def auto_tile(layout_mode):
    windows = get_windows()
    random.shuffle(windows)  # Shuffle the window order
    if layout_mode == "fibonacci":
        fibonacci_layout(windows)
    elif layout_mode == "vertical":
        vertical_layout(windows)

def main():
    # Listen for keypresses
    keyboard.add_hotkey('win+shift+w', lambda: launch_app("fibonacci"))
    keyboard.add_hotkey('win+shift+e', lambda: launch_app("vertical"))
    keyboard.add_hotkey('ctrl+win+up', lambda: auto_tile("vertical"))
    keyboard.add_hotkey('ctrl+win+down', lambda: auto_tile("fibonacci"))

    # Start the system tray icon in a separate thread
    tray_thread = threading.Thread(target=setup_tray_icon)
    tray_thread.daemon = True
    tray_thread.start()

    # Keep the script running to listen for keypresses
    keyboard.wait()

if __name__ == "__main__":
    main()