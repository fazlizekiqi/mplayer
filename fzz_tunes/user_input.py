# user_input.py
import time
from .os_compatibility import curses


class UserInputHandler:
    def __init__(self, window_manager):
        self.window_manager = window_manager

    def get_selected_music(self) -> int:
        max_y, max_x = self.window_manager.stdscr.getmaxyx()

        while True:
            user_input = ""
            enter_text = "Enter text: "
            y_bottom_position = max_y - 2
            self.window_manager.stdscr.addstr(y_bottom_position, 2, enter_text, curses.color_pair(3))
            self.window_manager.stdscr.move(y_bottom_position, 2 + len(enter_text))

            while True:
                key = self.window_manager.stdscr.getch()
                if key == 10:  # Enter key
                    break
                elif chr(key).isdigit():
                    user_input += chr(key)
                    self.window_manager.stdscr.addstr(chr(key))
                elif key == 127:  # Backspace key
                    if user_input:
                        user_input = user_input[:-1]
                        self.window_manager.stdscr.addstr("\b \b")  # Clear the character visually
                self.window_manager.stdscr.refresh()

            try:
                number = int(user_input)
                break
            except ValueError:
                self.window_manager.stdscr.addstr(y_bottom_position, 2, "Invalid input! Please enter a number.",
                                                  curses.color_pair(2))
                self.window_manager.stdscr.refresh()
                time.sleep(1)
                self.window_manager.stdscr.move(y_bottom_position, 2)
                self.window_manager.stdscr.clrtoeol()

        return user_input
