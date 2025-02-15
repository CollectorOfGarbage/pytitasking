import pygetwindow as gw
import pyautogui
import keyboard
import time

def get_windows():
    # Get all windows, including hidden ones, by removing the visibility check
    windows = gw.getWindowsWithTitle('')
    print(f"Detected {len(windows)} windows on the virtual desktop.")
    return windows

def fibonacci_layout():
    windows = get_windows()
    screen_width, screen_height = pyautogui.size()
    num_windows = len(windows)
    
    if num_windows == 0:
        print("No windows detected.")
        return
    
    x, y, w, h = 0, 0, screen_width, screen_height

    print("DAMN DANIEL" + str(screen_width) + " OK " + str(screen_height))
    for i, win in enumerate(windows):
        print(win.title)
        """ try:
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
            y += h """

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