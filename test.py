import pygetwindow as gw
import pyautogui
import math
import win32gui
import ctypes
from ctypes import wintypes
import tkinter as tk
from tkinter import messagebox, Frame, Label, Button, Scrollbar, Checkbutton, BooleanVar, StringVar, Canvas
from tkinter import LEFT, RIGHT, BOTH, X, Y, W, TOP, NW
import hashlib
import colorsys

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
        self.custom_order = []  # Keep track of custom window order
        self.preview_stringvars = {
            "title": StringVar(value=""),
            "size": StringVar(value=""),
            "position": StringVar(value=""),
        }
        
        # Variables for dragging
        self.drag_data = {"x": 0, "y": 0, "item": None, "index": -1}
        self.preview_items = []  # List of (rect_id, text_id, window_index)
        
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
        preview_label_frame = Frame(bottom_frame)
        preview_label_frame.pack(fill=X)
        
        Label(preview_label_frame, text="Layout Preview", font=("Arial", 12, "bold")).pack(side=LEFT)
        Label(preview_label_frame, 
              text="Drag windows to reorder them", 
              font=("Arial", 9, "italic"), 
              fg="gray").pack(side=LEFT, padx=10)
        
        self.preview_canvas = Canvas(bottom_frame, bg="lightgray", height=200)
        self.preview_canvas.pack(fill=X, expand=True, pady=5)
        
        # Bind events for dragging
        self.preview_canvas.tag_bind("window", "<ButtonPress-1>", self.on_drag_start)
        self.preview_canvas.tag_bind("window", "<B1-Motion>", self.on_drag_motion)
        self.preview_canvas.tag_bind("window", "<ButtonRelease-1>", self.on_drag_stop)
        
        # Buttons
        button_frame = Frame(main_frame)
        button_frame.pack(fill=X, pady=10)
        
        Button(button_frame, text="Clear All", command=self.clear_all).pack(side=LEFT, padx=5)
        Button(button_frame, text="Select All", command=self.select_all).pack(side=LEFT, padx=5)
        Button(button_frame, text="Reset Order", command=self.reset_order).pack(side=LEFT, padx=5)
        
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
                            command=lambda w=window, v=var: self.on_checkbox_toggle(w, v))
            cb.pack(side=LEFT, anchor=W)
            
            # Bind events to show preview when hovering over checkbox
            cb.bind("<Enter>", lambda event, w=window: self.show_preview(w))
            row_frame.bind("<Enter>", lambda event, w=window: self.show_preview(w))
    
    def on_checkbox_toggle(self, window, var):
        # Update the custom_order list when a checkbox is toggled
        if var.get():
            if window not in self.custom_order:
                self.custom_order.append(window)
        else:
            if window in self.custom_order:
                self.custom_order.remove(window)
        
        # Update the layout preview
        self.update_layout_preview()
    
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
        self.custom_order = []  # Clear custom order
        self.update_layout_preview()
    
    def select_all(self):
        for var in self.window_vars:
            var.set(True)
        self.update_custom_order()  # Update custom_order with all selected windows
        self.update_layout_preview()
    
    def reset_order(self):
        self.custom_order = []  # Reset to default order
        self.update_custom_order()  # Update custom_order with selected windows
        self.update_layout_preview()
    
    def get_selected_windows(self):
        # Filter custom_order to only include selected windows
        selected_windows = [win for win in self.custom_order if win in self.windows and self.window_vars[self.windows.index(win)].get()]
        
        if not selected_windows:
            # If no custom order, return windows in original order
            selected_windows = [win for i, win in enumerate(self.windows) if self.window_vars[i].get()]
        
        return selected_windows
    
    def update_custom_order(self):
        # Initialize custom_order with selected windows
        self.custom_order = [win for i, win in enumerate(self.windows) if self.window_vars[i].get()]
    
    def on_drag_start(self, event):
        # Record the item and its location
        for rect_id, text_id, index in self.preview_items:
            if self.preview_canvas.find_withtag("current")[0] in [rect_id, text_id]:
                self.drag_data["item"] = rect_id
                self.drag_data["text"] = text_id
                self.drag_data["index"] = index
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y
                
                # Raise the rectangle and text to the top
                self.preview_canvas.tag_raise(rect_id)
                self.preview_canvas.tag_raise(text_id)
                break
    
    def on_drag_motion(self, event):
        # Compute how much the mouse has moved
        if self.drag_data["item"] is not None:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            
            # Move the rectangle and text
            self.preview_canvas.move(self.drag_data["item"], dx, dy)
            self.preview_canvas.move(self.drag_data["text"], dx, dy)
            
            # Record the new position
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
    
    def on_drag_stop(self, event):
        if self.drag_data["item"] is not None:
            # Find which position this window should now be in
            rect_coords = self.preview_canvas.coords(self.drag_data["item"])
            rect_center_x = (rect_coords[0] + rect_coords[2]) / 2
            rect_center_y = (rect_coords[1] + rect_coords[3]) / 2
            
            # Get all selected windows
            selected_windows = self.get_selected_windows()
            
            closest_position = 0
            min_distance = float('inf')
            
            # Calculate layout for current number of windows
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            layout = calculate_layout_preview(len(selected_windows), canvas_width, canvas_height)
            
            # Find closest position
            for i, (x, y, w, h) in enumerate(layout):
                center_x = x + w/2
                center_y = y + h/2
                
                distance = math.sqrt((center_x - rect_center_x)**2 + (center_y - rect_center_y)**2)
                if distance < min_distance:
                    min_distance = distance
                    closest_position = i
            
            # Reorder the windows if position changed
            if closest_position != self.drag_data["index"]:
                # Get the window that was dragged
                dragged_window = selected_windows[self.drag_data["index"]]
                
                # Remove from old position
                selected_windows.pop(self.drag_data["index"])
                
                # Insert at new position
                if closest_position >= len(selected_windows):
                    selected_windows.append(dragged_window)
                else:
                    selected_windows.insert(closest_position, dragged_window)
                
                # Update custom order
                self.custom_order = selected_windows
                
                # Redraw the preview with the new order
                self.update_layout_preview()
            
            # Reset drag data
            self.drag_data = {"x": 0, "y": 0, "item": None, "text": None, "index": -1}
    
    def update_layout_preview(self):
        selected_windows = self.get_selected_windows()
        num_selected = len(selected_windows)
        
        # Clear canvas and reset items list
        self.preview_canvas.delete("all")
        self.preview_items = []
        
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
        
        # Fixed list of dark pastel tertiary colors
        tertiary_colors = [
            "#8B5E3B",  # Burnt Sienna (Red-Orange)
            "#556B2F",  # Dark Olive Green (Yellow-Green)
            "#6B5B95",  # Dusky Purple (Blue-Violet)
            "#8FBC8F",  # Dark Sea Green (Yellow-Green)
            "#D2691E",  # Chocolate (Red-Orange)
            "#4682B4",  # Steel Blue (Blue-Green)
            "#DA70D6",  # Orchid (Red-Violet)
            "#B8860B",  # Dark Goldenrod (Yellow-Orange)
            "#5F9EA0",  # Cadet Blue (Blue-Green)
            "#C71585",  # Medium Violet Red (Red-Violet)
            "#A52A2A",  # Brown (Red-Orange)
            "#2F4F4F",  # Dark Slate Gray (Blue-Green)
        ]

        # Persistent color mapping for each window title
        if not hasattr(self, "window_color_map"):
            self.window_color_map = {}

        # Track used colors to avoid duplicates
        used_colors = set(self.window_color_map.values())

        # Assign colors only if a window doesn't have one yet
        color_index = 0

        for i, (x, y, w, h) in enumerate(layout):
            window_title = selected_windows[i].title

            if window_title not in self.window_color_map:
                # Find the next unused color
                while tertiary_colors[color_index % len(tertiary_colors)] in used_colors:
                    color_index += 1
                
                color = tertiary_colors[color_index % len(tertiary_colors)]
                self.window_color_map[window_title] = color
                used_colors.add(color)
            else:
                color = self.window_color_map[window_title]  # Retrieve assigned color

            # Create rectangle
            rect_id = self.preview_canvas.create_rectangle(
                x, y, x+w, y+h, 
                fill=color, 
                outline="white", 
                width=2,
                tags=("window",)
            )

            # Create text (truncated if necessary)
            max_chars = max(5, w // 8)
            display_title = window_title[:max_chars] + "..." if len(window_title) > max_chars else window_title
            
            text_x = x + w//2
            text_y = y + h//2
            
            text_id = self.preview_canvas.create_text(
                text_x, text_y,
                text=display_title,
                fill="white" if i % 2 == 0 else "black",
                font=("Arial", 8, "bold"),
                tags=("window",)
            )
            
            self.preview_items.append((rect_id, text_id, i))
    
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