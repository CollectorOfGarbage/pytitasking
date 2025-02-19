# Pytitasking

Pytitasking is a window management application designed to help users organize and tile their open application windows efficiently. It provides a user-friendly GUI and system tray functionality for easy access and control.

## Features

- **Window Selection**: Choose which windows to tile and in what order.
- **Layout Options**: Supports Fibonacci and vertical layouts for window arrangement.
- **System Tray Icon**: Easily accessible from the system tray, allowing for quick actions like quitting the application.
- **Keyboard Shortcuts**: Launch the application and apply layouts using customizable keyboard shortcuts.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/pytitasking.git
   cd pytitasking
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command:
```
python src/main.py
```

Once the application is running, you can use the following keyboard shortcuts:

- `Win + Shift + W`: Launch the window selector with Fibonacci layout.
- `Win + Shift + E`: Launch the window selector with vertical layout.
- `Ctrl + Win + Up`: Automatically tile selected windows vertically.
- `Ctrl + Win + Down`: Automatically tile selected windows in Fibonacci layout.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.