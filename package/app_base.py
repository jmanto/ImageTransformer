CSS_FILE = "assets/style.css"

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

width = 600
height = 400

UNCHECKED_ICON = "assets/unchecked.png"
CHECKED_ICON = "assets/checked.png"


def window_corner(width, height):
    x = round((SCREEN_WIDTH - width) / 2)
    y = round((SCREEN_HEIGHT - height) / 2)
    return x, y

def apply_style():
    with open(CSS_FILE, "r") as f:
        style = f.read()

    return style