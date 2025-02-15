import pygetwindow as gw
import pyautogui
import keyboard
import time
import math
import win32gui
import ctypes
from ctypes import wintypes

def get_windows():
    """
    Get all windows from the current virtual desktop only.
    """
    # Load required Windows DLLs
    user32 = ctypes.WinDLL('user32')
    dwmapi = ctypes.WinDLL('dwmapi')
    
    # Define necessary constants and structures
    DWMWA_CLOAKED = 14
    
    # Get current virtual desktop identifier using VirtualDesktopAccessor.dll
    # Note: This would require the VirtualDesktopAccessor.dll to be installed and loaded
    # As an alternative approach, we'll filter based on window visibility and cloak status
    
    # Retrieve all windows using pygetwindow
    windows = gw.getWindowsWithTitle('')
    current_desktop_windows = []
    
    for win in windows:
        if not win.title or win.isMinimized or win.title == 'Program Manager':
            continue
        
        try:
            hwnd = win._hWnd
            
            # Check if window is visible
            if not win32gui.IsWindowVisible(hwnd):
                continue
                
            # Check if window is cloaked (hidden by the system)
            cloaked = wintypes.DWORD()
            dwmapi.DwmGetWindowAttribute(
                hwnd,
                DWMWA_CLOAKED,
                ctypes.byref(cloaked),
                ctypes.sizeof(cloaked)
            )
            
            if cloaked.value != 0:
                continue
                
            # If we made it here, the window is likely on the current desktop
            current_desktop_windows.append(win)
            
        except Exception as e:
            print(f"Error with window {win.title}: {e}")
    
    print(f"Detected {len(current_desktop_windows)} windows on current virtual desktop.")
    return current_desktop_windows

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
        print(len(windows))
        if i != len(windows)-1:
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
        else:
            #print("last window ")
            #print(x, y, w, h)
            try:
                print(f"Moving {win.title} to ({x}, {y}), size ({w}x{h})")
                win.moveTo(x, y)
                win.resizeTo(w, h)
                x = x + w 
            except Exception as e:
                print(f"Could not move {win.title}: {e}")

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