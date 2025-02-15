import pygetwindow as gw
import pyautogui
import keyboard
import time
import math

def get_windows():
    # Get all windows and filter out irrelevant ones (minimized, system-related, etc.)
    windows = gw.getWindowsWithTitle('')
    filtered_windows = [win for win in windows if win.title and not win.isMinimized]
    print(f"Detected {len(filtered_windows)} relevant windows.")
    return filtered_windows

def fibonacci_layout():
    windows = get_windows()
    for i in windows:
        print(i.title)
    screen_width, screen_height = pyautogui.size()
    screen_height = screen_height - 50
    num_windows = len(windows)
    
    if num_windows == 0:
        print("No windows detected.")
        return
    
    x, y, w, h = 0, 0, screen_width, screen_height

    for i, win in enumerate(windows):
        if i % 2 == 0:
            ## even windows left
            w = math.floor(w/2)
            try:
                print(f"Moving {win.title} to ({x}, {y}), size ({w}x{h})")
                win.moveTo(x, y)
                win.resizeTo(w, h)
                x = x + w 
            except Exception as e:
                print(f"Could not move {win.title}: {e}")
        else:
            ## odd windows top
            h = math.floor(h/2)
            try:
                print(f"Moving {win.title} to ({x}, {y}), size ({w}x{h})")
                win.moveTo(x, y)
                win.resizeTo(w, h)
                y = y + h
            except Exception as e:
                print(f"Could not move {win.title}: {e}")

        """ try:
            print(f"Moving {win.title} to ({x}, {y}), size ({w}x{h})")
            win.moveTo(x, y)
            win.resizeTo(w, h)
        except Exception as e:
            print(f"Could not move {win.title}: {e}")

        # Update the position and size for the next window
        if i % 2 == 0:  # Adjust width for even-indexed windows
            x += w  # Move x to the right by the width of the current window
            w //= 2  # Half the width for the next window
            # Check if the next window will be off-screen horizontally
            if x + w > screen_width:
                x = 0  # Reset to the left edge
                y += h  # Move down to the next row
                h //= 2  # Half the height for the next window if we move to the next row
        else:  # Adjust height for odd-indexed windows
            y += h  # Move y down by the height of the current window
            h //= 2  # Half the height for the next window
            # Check if the next window will be off-screen vertically
            if y + h > screen_height:
                break  # Stop if we've run out of space on the screen """

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