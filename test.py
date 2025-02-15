import pygetwindow as gw
import pyautogui
import math
import win32gui
import ctypes
from ctypes import wintypes
import tkinter as tk
from tkinter import messagebox, Frame, Label, Button, Scrollbar, Checkbutton, BooleanVar, StringVar, Canvas
from tkinter import LEFT, RIGHT, BOTH, X, Y, W, TOP, NW

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
            
            # Check if the window is off-screen
            rect = win32gui.GetWindowRect(hwnd)
            if rect[0] < -100 or rect[1] < -100:  # Window is off-screen
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
    screen_height = screen_height - 50  # Account for taskbar
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

# Function to calculate Fibonacci layout coordinates for preview
def calculate_layout_preview(num_windows, canvas_width, canvas_height):
    if num_windows == 0:
        return []
    
    layout = []
    x, y, w, h = 0, 0, canvas_width, canvas_height
    
    for i in range(num_windows):
        if i != num_windows - 1:
            if i % 2 == 0:
                # Even windows: split horizontally
                w = math.floor(w / 2)
                layout.append((x, y, w, h))
                x += w
            else:
                # Odd windows: split vertically
                h = math.floor(h / 2)
                layout.append((x, y, w, h))
                y += h
        else:
            layout.append((x, y, w, h))
    
    return layout

# GUI with checkboxes and layout preview
class WindowSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows Fibonacci Layout")
        self.root.geometry("900x650")
        
        self.windows = get_windows()
        self.window_vars = []  # BooleanVars for checkboxes
        self.preview_stringvars = {
            "title": StringVar(value=""),
            "size": StringVar(value=""),
            "position": StringVar(value=""),
        }
        
        # Main frame
        main_frame = Frame(root, padx=10, pady=10)
        main_frame.pack(fill=BOTH, expand=True)
        
        # Top section split into left (selection) and right (window preview) panes
        top_frame = Frame(main_frame)
        top_frame.pack(fill=X, expand=True)
        
        left_frame = Frame(top_frame)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        right_frame = Frame(top_frame, padx=10, width=300)
        right_frame.pack(side=RIGHT, fill=Y)
        right_frame.pack_propagate(False)  # Maintain width
        
        # Bottom section for layout preview
        bottom_frame = Frame(main_frame, pady=10)
        bottom_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # Selection pane
        Label(left_frame, 
              text="Select windows in the order you want them tiled:",
              font=("Arial", 11)).pack(anchor=W, pady=(0, 5))
        
        # Scrollable frame for checkboxes
        scroll_frame = Frame(left_frame)
        scroll_frame.pack(fill=BOTH, expand=True)
        
        scrollbar = Scrollbar(scroll_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.canvas = Canvas(scroll_frame, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.canvas.yview)
        
        self.checkbox_frame = Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.checkbox_frame, anchor='nw')
        
        # Create checkboxes for each window
        self.create_checkboxes()
        
        # Configure canvas scrolling
        self.checkbox_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Window preview pane
        Label(right_frame, text="Window Information", font=("Arial", 12, "bold")).pack(anchor=W, pady=(0, 10))
        
        preview_box = Frame(right_frame, bd=1, relief=tk.SOLID, padx=10, pady=10)
        preview_box.pack(fill=X, padx=5, pady=5)
        
        Label(preview_box, text="Title:").pack(anchor=W, pady=2)
        Label(preview_box, textvariable=self.preview_stringvars["title"], wraplength=270).pack(anchor=W, pady=(0, 5))
        
        Label(preview_box, text="Size:").pack(anchor=W, pady=2)
        Label(preview_box, textvariable=self.preview_stringvars["size"]).pack(anchor=W, pady=(0, 5))
        
        Label(preview_box, text="Position:").pack(anchor=W, pady=2)
        Label(preview_box, textvariable=self.preview_stringvars["position"]).pack(anchor=W, pady=(0, 5))
        
        # Layout preview section
        Label(bottom_frame, text="Layout Preview", font=("Arial", 12, "bold")).pack(anchor=W)
        
        self.preview_canvas = Canvas(bottom_frame, bg="lightgray", height=200)
        self.preview_canvas.pack(fill=X, expand=True, pady=5)
        
        # Buttons
        button_frame = Frame(main_frame)
        button_frame.pack(fill=X, pady=10)
        
        Button(button_frame, text="Clear All", command=self.clear_all).pack(side=LEFT, padx=5)
        Button(button_frame, text="Select All", command=self.select_all).pack(side=LEFT, padx=5)
        Button(button_frame, text="Update Preview", command=self.update_layout_preview).pack(side=LEFT, padx=5)
        
        Button(button_frame, 
               text="Apply Fibonacci Layout", 
               command=self.apply_tiling,
               bg="#4CAF50", 
               fg="white",
               font=("Arial", 11, "bold"), 
               padx=10, 
               pady=5).pack(side=RIGHT, padx=5)
        
        # Initialize preview
        self.update_layout_preview()
    
    def create_checkboxes(self):
        # Clear existing checkboxes if any
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()
        
        self.window_vars = []
        
        for i, window in enumerate(self.windows):
            var = BooleanVar()
            self.window_vars.append(var)
            
            row_frame = Frame(self.checkbox_frame)
            row_frame.pack(fill=X, pady=2)
            
            cb = Checkbutton(row_frame, variable=var, text=window.title, 
                            command=self.update_layout_preview)
            cb.pack(side=LEFT, anchor=W)
            
            # Bind events to show preview when hovering over checkbox
            cb.bind("<Enter>", lambda event, w=window: self.show_preview(w))
            row_frame.bind("<Enter>", lambda event, w=window: self.show_preview(w))
    
    def show_preview(self, window):
        self.preview_stringvars["title"].set(window.title)
        self.preview_stringvars["size"].set(f"{window.width} x {window.height}")
        self.preview_stringvars["position"].set(f"({window.left}, {window.top})")
    
    def on_frame_configure(self, event):
        # Update the scrollregion to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        # Update the width of the window
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def clear_all(self):
        for var in self.window_vars:
            var.set(False)
        self.update_layout_preview()
    
    def select_all(self):
        for var in self.window_vars:
            var.set(True)
        self.update_layout_preview()
    
    def get_selected_windows(self):
        selected_windows = []
        for i, var in enumerate(self.window_vars):
            if var.get():
                selected_windows.append(self.windows[i])
        return selected_windows
    
    def update_layout_preview(self):
        selected_windows = self.get_selected_windows()
        num_selected = len(selected_windows)
        
        # Clear canvas
        self.preview_canvas.delete("all")
        
        if num_selected == 0:
            self.preview_canvas.create_text(
                self.preview_canvas.winfo_width() // 2,
                self.preview_canvas.winfo_height() // 2,
                text="No windows selected",
                fill="gray"
            )
            return
        
        # Get canvas dimensions
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        # If canvas hasn't been rendered yet, use default size
        if canvas_width < 10:
            canvas_width = 800
        if canvas_height < 10:
            canvas_height = 200
        
        # Calculate layout
        layout = calculate_layout_preview(num_selected, canvas_width, canvas_height)
        
        # Draw rectangles for each window
        colors = ["#4CAF50", "#2196F3", "#FFC107", "#FF5722", "#9C27B0", "#E91E63", "#00BCD4"]
        
        for i, (x, y, w, h) in enumerate(layout):
            color = colors[i % len(colors)]
            window_title = selected_windows[i].title
            
            # Create rectangle
            self.preview_canvas.create_rectangle(x, y, x+w, y+h, fill=color, outline="white", width=2)
            
            # Create text (truncated if necessary)
            max_chars = max(5, w // 8)  # Rough estimate for fitting text
            display_title = window_title[:max_chars] + "..." if len(window_title) > max_chars else window_title
            
            text_x = x + w//2
            text_y = y + h//2
            
            self.preview_canvas.create_text(
                text_x, text_y,
                text=display_title,
                fill="white" if i % 2 == 0 else "black",
                font=("Arial", 8, "bold")
            )
    
    def apply_tiling(self):
        selected_windows = self.get_selected_windows()
        
        if not selected_windows:
            messagebox.showwarning("No Selection", "Please select at least one window to tile.")
            return
        
        fibonacci_layout(selected_windows)

# Main function to run the GUI
def main():
    root = tk.Tk()
    app = WindowSelectorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()