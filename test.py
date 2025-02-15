import pygetwindow as gw
import pyautogui
import pywinctl
import keyboard
import time

def get_windows():
    windows = [win for win in gw.getWindowsWithTitle('') if win.visible]
    print(f"Detected {len(windows)} visible windows.")
    return windows

def fibonacci_layout():
    windows = get_windows()
    screen_width, screen_height = pyautogui.size()
    num_windows = len(windows)
    
    if num_windows == 0:
        print("No visible windows detected.")
        return
    
    x, y, w, h = 0, 0, screen_width, screen_height
    for i, win in enumerate(windows):
        try:
            print(f"Moving {win.title} to ({x}, {y}), size ({w}x{h})")
            win.moveTo(x, y)
            win.resizeTo(w, h)
        except Exception as e:
            print(f"Could not move {win.title}: {e}")
        
        if i % 2 == 0:
            w //= 2
            x += w
        else:
            h //= 2
            y += h

def main():
    print("Tiling Window Manager started. Press Win+Shift+W to toggle Fibonacci mode.")
    keyboard.add_hotkey("win+shift+w", fibonacci_layout)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()