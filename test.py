import pygetwindow as gw
import pyautogui
import keyboard
import time
import math
import win32gui
import ctypes
from ctypes import wintypes
import tkinter as tk
from tkinter import messagebox

# Function to get visible windows on the current virtual desktop
def get_windows():
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
            dwmapi = ctypes.WinDLL('dwmapi')
            DWMWA_CLOAKED = 14
            cloaked = wintypes.DWORD()
            dwmapi.DwmGetWindowAttribute(
                hwnd,
                DWMWA_CLOAKED,
                ctypes.byref(cloaked),
                ctypes.sizeof(cloaked)
            )
            
            if cloaked.value != 0:
                continue
                
            # If the window is visible and not cloaked, add it to the list
            current_desktop_windows.append(win)
            
        except Exception as e:
            print(f"Error with window {win.title}: {e}")
    
    print(f"Detected {len(current_desktop_windows)} windows on current virtual desktop.")
    return current_desktop_windows

# Function to apply Fibonacci layout to selected windows
def fibonacci_layout(selected_windows):
    screen_width, screen_height = pyautogui.size()
    screen_height = screen_height - 50
    num_windows = len(selected_windows)
    
    if num_windows == 0:
        print("No windows detected.")
        return
    
    x, y, w, h = 0, 0, screen_width, screen_height

    for i, win in enumerate(selected_windows):
        if i != len(selected_windows) - 1:
            if i % 2 == 0:
                # Even windows: split horizontally
                w = math.floor(w / 2)
                try:
                    print(f"Moving {win.title} to ({x}, {y}), size ({w}x{h})")
                    win.moveTo(x, y)
                    win.resizeTo(w, h)
                    x += w 
                except Exception as e:
                    print(f"Could not move {win.title}: {e}")
            else:
                # Odd windows: split vertically
                h = math.floor(h / 2)
                try:
                    print(f"Moving {win.title} to ({x}, {y}), size ({w}x{h})")
                    win.moveTo(x, y)
                    win.resizeTo(w, h)
                    y += h
                except Exception as e:
                    print(f"Could not move {win.title}: {e}")
        else:
            try:
                print(f"Moving {win.title} to ({x}, {y}), size ({w}x{h})")
                win.moveTo(x, y)
                win.resizeTo(w, h)
                x += w 
            except Exception as e:
                print(f"Could not move {win.title}: {e}")

# GUI for selecting windows to tile
class WindowSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Select Windows to Tile")
        
        self.selected_windows = []
        self.windows = get_windows()
        
        self.checkboxes = {}
        
        # Create a label and checkboxes for the windows
        label = tk.Label(root, text="Select the windows to tile:")
        label.pack(padx=10, pady=10)
        
        for win in self.windows:
            var = tk.BooleanVar()
            checkbox = tk.Checkbutton(root, text=win.title, variable=var)
            checkbox.pack(anchor="w")
            self.checkboxes[win.title] = var  # Use the window title as the key
        
        # Create a button to apply the tiling layout
        tile_button = tk.Button(root, text="Apply Fibonacci Layout", command=self.apply_tiling)
        tile_button.pack(pady=20)
    
    def apply_tiling(self):
        # Collect selected windows based on the checkbox status
        self.selected_windows = [win for win in self.windows if self.checkboxes[win.title].get()]
        
        if not self.selected_windows:
            messagebox.showwarning("No Selection", "Please select at least one window to tile.")
        else:
            fibonacci_layout(self.selected_windows)

# Main function to run the GUI
def main():
    root = tk.Tk()
    app = WindowSelectorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()