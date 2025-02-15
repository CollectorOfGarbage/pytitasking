import win32gui
import win32con
import win32api
import keyboard
import sys
from typing import Dict, List, Tuple
import json
import os
from enum import Enum

class Layout(Enum):
    GRID = "grid"
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    MAIN_AND_STACK = "main_and_stack"
    FIBONACCI = "fibonacci"
    MONOCLE = "monocle"

class TilingWindowManager:
    def __init__(self):
        self.managed_windows: Dict[int, dict] = {}
        self.current_layout = Layout.GRID
        self.main_ratio = 0.6  # For main_and_stack layout
        self.padding = 5
        self.load_config()
        
        # Get primary monitor dimensions
        monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0, 0)))
        work_area = monitor_info.get("Work")
        self.screen_width = work_area[2] - work_area[0]
        self.screen_height = work_area[3] - work_area[1]
        
        # Store last active window
        self.last_active = None
        self.ignored_windows = set()

    def load_config(self):
        """Load configuration from file or create default."""
        config_path = os.path.expanduser("~/.tiling_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                self.padding = config.get('padding', 5)
                self.main_ratio = config.get('main_ratio', 0.6)
                layout_name = config.get('current_layout', 'GRID')
                try:
                    self.current_layout = Layout[layout_name]
                except:
                    self.current_layout = Layout.GRID
            except:
                pass

    def save_config(self):
        """Save current configuration."""
        config_path = os.path.expanduser("~/.tiling_config.json")
        config = {
            'padding': self.padding,
            'main_ratio': self.main_ratio,
            'current_layout': self.current_layout.name
        }
        with open(config_path, 'w') as f:
            json.dump(config, f)

    def is_valid_window(self, hwnd: int) -> bool:
        if not win32gui.IsWindowVisible(hwnd):
            return False
        
        if hwnd in self.ignored_windows:
            return False
            
        excluded_classes = [
            'Progman', 'Button', 'Shell_TrayWnd', 'Windows.UI.Core.CoreWindow',
            'ApplicationFrameWindow', 'Windows.UI.Core.CoreWindow'
        ]
        class_name = win32gui.GetClassName(hwnd)
        if class_name in excluded_classes:
            return False
            
        if win32gui.GetWindowText(hwnd) == "":
            return False
            
        placement = win32gui.GetWindowPlacement(hwnd)
        if placement[1] == win32con.SW_SHOWMINIMIZED:
            return False
            
        return True

    def get_visible_windows(self) -> List[int]:
        def callback(hwnd: int, windows: List[int]):
            if self.is_valid_window(hwnd):
                windows.append(hwnd)
            return True
            
        windows = []
        win32gui.EnumWindows(callback, windows)
        return windows

    def set_layout(self, layout: Layout):
        """Set specific layout."""
        self.current_layout = layout
        self.tile_windows()
        print(f"Switched to {layout.value} layout")

    def cycle_layout(self):
        """Cycle through available layouts."""
        layouts = list(Layout)
        current_index = layouts.index(self.current_layout)
        self.current_layout = layouts[(current_index + 1) % len(layouts)]
        self.tile_windows()
        print(f"Switched to {self.current_layout.value} layout")

    def adjust_main_ratio(self, increase: bool):
        """Adjust the main window ratio for main_and_stack layout."""
        delta = 0.05
        if increase:
            self.main_ratio = min(0.9, self.main_ratio + delta)
        else:
            self.main_ratio = max(0.1, self.main_ratio - delta)
        self.tile_windows()

    def toggle_window(self):
        """Toggle current window in/out of tiling."""
        hwnd = win32gui.GetForegroundWindow()
        if hwnd in self.ignored_windows:
            self.ignored_windows.remove(hwnd)
            print("Window added to tiling")
        else:
            self.ignored_windows.add(hwnd)
            print("Window removed from tiling")
        self.tile_windows()

    def apply_monocle_layout(self, windows: List[int]):
        """Apply monocle layout - only show active window full screen."""
        active_window = win32gui.GetForegroundWindow()
        if active_window in windows:
            # Place active window in full screen
            win32gui.SetWindowPos(active_window, win32con.HWND_TOP,
                                0, 0,
                                self.screen_width - self.padding,
                                self.screen_height - self.padding,
                                win32con.SWP_SHOWWINDOW)
            
            # Minimize other windows
            for hwnd in windows:
                if hwnd != active_window:
                    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        elif windows:
            # If active window is not in our list, use first window
            win32gui.SetWindowPos(windows[0], win32con.HWND_TOP,
                                0, 0,
                                self.screen_width - self.padding,
                                self.screen_height - self.padding,
                                win32con.SWP_SHOWWINDOW)
            
            # Minimize other windows
            for hwnd in windows[1:]:
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)

    def apply_fibonacci_layout(self, windows: List[int]):
        """Apply Fibonacci spiral layout."""
        if not windows:
            return
            
        if len(windows) == 1:
            win32gui.SetWindowPos(windows[0], win32con.HWND_TOP,
                                0, 0,
                                self.screen_width - self.padding,
                                self.screen_height - self.padding,
                                win32con.SWP_SHOWWINDOW)
            return
            
        # First window gets half the screen
        win32gui.SetWindowPos(windows[0], win32con.HWND_TOP,
                            0, 0,
                            self.screen_width // 2 - self.padding,
                            self.screen_height - self.padding,
                            win32con.SWP_SHOWWINDOW)
        
        remaining_width = self.screen_width - (self.screen_width // 2)
        remaining_height = self.screen_height
        x_offset = self.screen_width // 2
        y_offset = 0
        
        # Handle remaining windows in decreasing sizes
        for i, hwnd in enumerate(windows[1:], 1):
            if i % 2 == 1:  # Horizontal split
                height = remaining_height // 2
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOP,
                                    x_offset, y_offset,
                                    remaining_width - self.padding,
                                    height - self.padding,
                                    win32con.SWP_SHOWWINDOW)
                remaining_height = remaining_height - height
                y_offset += height
            else:  # Vertical split
                width = remaining_width // 2
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOP,
                                    x_offset, y_offset,
                                    width - self.padding,
                                    remaining_height - self.padding,
                                    win32con.SWP_SHOWWINDOW)
                remaining_width = remaining_width - width
                x_offset += width

    def apply_layout(self, windows: List[int]):
        """Apply the current layout to windows."""
        if not windows:
            return

        if self.current_layout == Layout.HORIZONTAL:
            width = self.screen_width // len(windows)
            for i, hwnd in enumerate(windows):
                x = i * width
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOP,
                                    x, 0, 
                                    width - self.padding,
                                    self.screen_height - self.padding,
                                    win32con.SWP_SHOWWINDOW)

        elif self.current_layout == Layout.VERTICAL:
            height = self.screen_height // len(windows)
            for i, hwnd in enumerate(windows):
                y = i * height
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOP,
                                    0, y,
                                    self.screen_width - self.padding,
                                    height - self.padding,
                                    win32con.SWP_SHOWWINDOW)

        elif self.current_layout == Layout.MAIN_AND_STACK:
            if len(windows) == 1:
                win32gui.SetWindowPos(windows[0], win32con.HWND_TOP,
                                    0, 0,
                                    self.screen_width - self.padding,
                                    self.screen_height - self.padding,
                                    win32con.SWP_SHOWWINDOW)
            else:
                # Main window
                main_width = int(self.screen_width * self.main_ratio)
                win32gui.SetWindowPos(windows[0], win32con.HWND_TOP,
                                    0, 0,
                                    main_width - self.padding,
                                    self.screen_height - self.padding,
                                    win32con.SWP_SHOWWINDOW)
                
                # Stack windows
                stack_width = self.screen_width - main_width
                stack_height = self.screen_height // (len(windows) - 1)
                
                for i, hwnd in enumerate(windows[1:], 1):
                    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP,
                                        main_width,
                                        (i-1) * stack_height,
                                        stack_width - self.padding,
                                        stack_height - self.padding,
                                        win32con.SWP_SHOWWINDOW)
        
        elif self.current_layout == Layout.FIBONACCI:
            self.apply_fibonacci_layout(windows)
            
        elif self.current_layout == Layout.MONOCLE:
            self.apply_monocle_layout(windows)

        else:  # Grid layout (default)
            num_windows = len(windows)
            cols = round(num_windows ** 0.5)
            rows = (num_windows + cols - 1) // cols
            
            cell_width = self.screen_width // cols
            cell_height = self.screen_height // rows
            
            for i, hwnd in enumerate(windows):
                row = i // cols
                col = i % cols
                
                x = col * cell_width
                y = row * cell_height
                
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOP,
                                    x, y,
                                    cell_width - self.padding,
                                    cell_height - self.padding,
                                    win32con.SWP_SHOWWINDOW)

    def tile_windows(self):
        """Arrange windows according to current layout."""
        windows = self.get_visible_windows()
        if windows:
            self.apply_layout(windows)

    def print_help(self):
        """Print help information."""
        print("\nTiling Window Manager Hotkeys:")
        print("Win + Shift + T: Tile windows with current layout")
        print("Win + Shift + Space: Cycle through layouts")
        print("Win + Shift + [: Decrease main window size")
        print("Win + Shift + ]: Increase main window size")
        print("Win + Shift + X: Toggle current window in/out of tiling")
        print("\nLayouts:")
        for i, layout in enumerate(Layout):
            print(f"Win + Shift + {i+1}: Switch to {layout.value} layout")
        print("\nWin + Shift + H: Show this help")
        print("Ctrl + C: Exit")

    def run(self):
        """Main loop with hotkey handling."""
        print("Multi-Layout Tiling Window Manager Started")
        self.print_help()
        
        # Register layout switching hotkeys
        for i, layout in enumerate(Layout):
            keyboard.add_hotkey(f'windows+shift+{i+1}', lambda l=layout: self.set_layout(l))
        
        # Register other hotkeys
        keyboard.add_hotkey('windows+shift+t', self.tile_windows)
        keyboard.add_hotkey('windows+shift+space', self.cycle_layout)
        keyboard.add_hotkey('windows+shift+[', lambda: self.adjust_main_ratio(False))
        keyboard.add_hotkey('windows+shift+]', lambda: self.adjust_main_ratio(True))
        keyboard.add_hotkey('windows+shift+x', self.toggle_window)
        keyboard.add_hotkey('windows+shift+h', self.print_help)
        
        try:
            keyboard.wait('ctrl+c')
        except KeyboardInterrupt:
            pass
        finally:
            print("\nSaving configuration and exiting...")
            self.save_config()
            sys.exit(0)

if __name__ == "__main__":
    manager = TilingWindowManager()
    manager.run()