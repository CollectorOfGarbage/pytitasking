from PIL import Image, ImageDraw, ImageFont
import pystray
from pystray import MenuItem, Icon
import sys

def create_image():
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), (211, 211, 211))  # Light grey background
    dc = ImageDraw.Draw(image)
    
    # Load a font
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw a blue "M" in the center
    text = "M"
    text_width, text_height = dc.textsize(text, font=font)
    position = ((width - text_width) // 2, (height - text_height) // 2)
    dc.text(position, text, fill=(0, 0, 255), font=font)  # Blue color
    
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