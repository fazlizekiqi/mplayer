# windows.py
import time
from .os_compatibility import curses
from curses.textpad import rectangle, Textbox


class WindowManager:
    def __init__(self):
        self.search_box = None
        self.window = curses.newwin(curses.LINES - 1, curses.COLS - 1, 1, 1)
        curses.start_color()  # Enable color
        curses.use_default_colors()  # Use terminal default colors
        self.add_border()
        self.refresh()
        self.max_y, self.max_x = self.window.getmaxyx()

    def add_border(self):
        self.window.border()

    def refresh(self):
        self.window.refresh()

    def getch(self):
        return self.window.getch()

    def clear(self):
        self.window.clear()

    def get_maxyx(self):
        return self.window.getmaxyx()

    def addstr(self, str):
        self.window.addstr(str)

    def addstr_with_xy(self, y, x, text, color):
        self.window.addstr(y, x, text, color)

    def add_author(self):
        author = "Author: Fazli Zekiqi"
        self.window.addstr(curses.LINES - 3, int(curses.COLS - 2 - len(author)), author, curses.color_pair(3))

    def add_banner(self):
        mPlayer_art = [
            "       __________.__                             ",
            "  _____\\______   |  | _____  ___.__. ___________ ",
            " /     \\|     ___|  | \\__  \\<   |  _/ __ \\_  __ \\",
            "|  Y Y  |    |   |  |__/ __ \\___  \\  ___/|  | \\/",
            "|__|_|  |____|   |____(____  / ____|\\___  |__|   ",
            "      \\/                   \\/\\/         \\/       "
        ]

        # Calculate position for "mPlayer" text
        y_text = int(curses.LINES / 2 / 2) - len(mPlayer_art) // 2
        x_text = int((curses.COLS - len(mPlayer_art[0])) / 2)

        for i, line in enumerate(mPlayer_art):
            self.window.addstr(y_text + i, x_text, line, curses.color_pair(1))

    def add_search_box(self):
        rect_height = 2
        rect_width = 60
        y = int((curses.LINES - rect_height) / 2)
        x = int((curses.COLS - rect_width) / 2)

        self.window.attron(curses.color_pair(1))
        rectangle(self.window, y, x, y + rect_height, x + rect_width)
        self.window.attroff(curses.color_pair(1))

        search_box_win = self.window.derwin(1, rect_width - 2, y + 1, x + 1)
        self.search_box = Textbox(search_box_win)

    def get_user_search(self):
        self.search_box.edit()
        return self.search_box.gather()

    def add_select_music_field(self):
        enter_text = "Select music: "
        y_bottom_position = self.max_y - 2
        self.window.addstr(y_bottom_position, 2, enter_text, curses.color_pair(3))
        self.window.move(y_bottom_position, 2 + len(enter_text))

    def render_list_items(self, list):
        for i, item in enumerate(list):
            self.window.addstr(2 + i, 2, f"{i + 1}:  {item.title} ({item.duration}) \n", curses.color_pair(1))

    def add_error_message(self):
        self.window.addstr(self.max_y - 2, 2, "Invalid input! Please enter a number.", curses.color_pair(2))
        self.window.refresh()
        time.sleep(1)
        self.window.move(self.max_y - 2, 2)
        self.window.clrtoeol()

    def add_loading_message(self):
        message = "Preparing your music to play..."
        y = int(curses.LINES / 2)
        x = int((curses.COLS - len(message)) / 2)
        self.clear()
        self.window.addstr(y, x, message, curses.color_pair(1))
        self.refresh()

    def add_music_details(self, currently_playing_name):
        self.window.addstr(0, 0, f"Music playing: {currently_playing_name:<30}", curses.color_pair(1))

    def add_music_player_instructions(self):
        self.window.addstr(3, 0, "[p] Play/Pause        [r] Rewind          [b] Go back                 ",
                           curses.color_pair(3))
        self.window.addstr(4, 0, "[+] Increase Volume   [-] Decrease Volume [q] Quit                 ",
                           curses.color_pair(3))
        self.window.addstr(5, 0, "[s] Search                 ",
                           curses.color_pair(3))

    def progress_bar(self, progress_seconds, progress_minutes, seconds_left, duration):
        self.window.addstr(1, 0, f"Progress: {progress_minutes:02d}:{seconds_left:02d}  ", curses.color_pair(2))
        duration_minutes, duration_seconds = map(int, duration.split(':'))
        duration_in_seconds = duration_minutes * 60 + duration_seconds
        progress_percent = min(progress_seconds / duration_in_seconds, 1.0)

        # Length of the progress bar (adjust as needed)
        bar_length = 50
        filled_length = int(bar_length * progress_percent)
        bar = '█' * filled_length + ' ' * (bar_length - filled_length)

        self.window.addstr(2, 0, '[%s] %d:%02d/%d:%02d' % (
            bar, progress_minutes, seconds_left, duration_in_seconds // 60, duration_in_seconds % 60),
                           curses.color_pair(1))
