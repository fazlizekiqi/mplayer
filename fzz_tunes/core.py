# core.py
import os
from pygame import mixer
import threading
import time
import curses

from .configs import default_config


class MusicPlayer:
    def __init__(self):
        self.player = mixer
        self.player.init()

    def play_music(self, file_path):
        self.player.music.load(file_path)
        self.player.music.set_volume(default_config["default_vol"])
        self.player.music.play()

    def stop_music(self):
        self.player.music.stop()

    def pause_music(self):
        self.player.music.pause()

    def unpause_music(self):
        self.player.music.unpause()

    def set_volume(self, volume):
        self.player.music.set_volume(volume)

    def exit_player(self, window):
        self.player.stop_music()
        window.addstr("Stopping music\n")
        window.refresh()
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        os._exit(0)


def listen_for_input(window, player):
    hotkeys = {
        ord('p'): player.pause_music,
        ord('r'): player.player.music.rewind,
        ord('s'): player.stop_music,
        ord('+'): lambda: player.set_volume(player.player.music.get_volume() + 0.1),
        ord('-'): lambda: player.set_volume(player.player.music.get_volume() - 0.1),
        ord('q'): player.exit_player,
        3: player.exit_player  # Ctrl+C
    }

    curses.start_color()  # Enable color
    curses.use_default_colors()  # Use terminal default colors
    while True:
        key = window.getch()
        if key in hotkeys:
            hotkeys[key]()



