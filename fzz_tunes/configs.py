import  curses

# configs.py
default_config = {"music_file_location": "./mp3", "default_vol": 0.5}

def init_curses_colors():
    curses.start_color()  # Enable color
    curses.use_default_colors()  # Use terminal default colors
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)