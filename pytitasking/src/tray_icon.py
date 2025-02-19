from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem, Icon
import sys

def create_image():
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), (255, 255, 255))
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 4, height // 4, width * 3 // 4, height * 3 // 4),
        fill=(0, 0, 0))
    return image

def on_quit(icon, item):
    icon.stop()
    sys.exit(0)

def setup_tray_icon():
    icon = Icon("pytitasking")
    icon.icon = create_image()
    icon.title = "Pytitasking"
    icon.menu = pystray.Menu(
        MenuItem("Quit", on_quit)
    )
    icon.run()