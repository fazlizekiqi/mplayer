import os
from curses.textpad import rectangle, Textbox
import curses
import time
from .search_youtube import SearchYoutube
from pytube import YouTube
from pygame import mixer
from moviepy.editor import AudioFileClip
import threading
from mutagen.mp3 import MP3
import ffmpeg
from scipy.io.wavfile import read

default_config = {"music_file_location": "./mp3", "default_vol": 0.5}
player = mixer


def main():
    import ssl
    ssl._create_default_https_context = ssl._create_stdlib_context

    location_ = default_config['music_file_location']
    for file in os.listdir(location_):
        file_path = os.path.join(location_, file)
        os.remove(file_path)
    curses.wrapper(add_screen)


def add_screen(stdscr):
    curses.start_color()  # Enable color
    curses.use_default_colors()  # Use terminal default colors
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)

    GREEN_AND_BLACK = curses.color_pair(1)
    RED_AND_BLACK = curses.color_pair(2)
    CYAN_AND_BLACK = curses.color_pair(3)

    window = curses.newwin(curses.LINES - 1, curses.COLS - 1, 1, 1)
    window.border()

    author = "Author: Fazli Zekiqi"
    window.addstr(curses.LINES - 3, int(curses.COLS - 2 - len(author)), author, curses.color_pair(3))

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
        window.addstr(y_text + i, x_text, line, GREEN_AND_BLACK)

    # Calculate the coordinates for the rectangle
    rect_height = 2
    rect_width = 60
    y = int((curses.LINES - rect_height) / 2)
    x = int((curses.COLS - rect_width) / 2)

    window.attron(GREEN_AND_BLACK)
    rectangle(window, y, x, y + rect_height, x + rect_width)
    window.attroff(GREEN_AND_BLACK)

    search_box_win = window.derwin(1, rect_width - 2, y + 1, x + 1)
    search_box = Textbox(search_box_win)
    window.refresh()

    search_box.edit()

    input_search = search_box.gather()

    # Clear the search screen
    window.clear()
    window.border()
    window.refresh()

    # SCENE 2: Choose music

    curses.init_pair(1, curses.COLOR_GREEN, -1)
    GREEN_AND_BLACK = curses.color_pair(1)

    search_youtube = SearchYoutube()
    results = search_youtube.search(input_search)

    for i, item in enumerate(results):
        window.addstr(2 + i, 2, f"{i + 1}:  {item.title}+ \n", GREEN_AND_BLACK)

    selected_music = int(get_selected_music(window))

    # SCENE 3: Play Music
    message = "Preparing your music to play..."
    y = int(curses.LINES / 2)
    x = int((curses.COLS - len(message)) / 2)
    window.clear()
    window.addstr(y, x, message, curses.color_pair(1))
    window.refresh()

    # Downloadd
    yt = YouTube(results[selected_music - 1].link,
                 on_progress_callback=downloading(window),
                 on_complete_callback=downloaded(window),
                 # proxies=my_proxies,
                 # use_oauth=False,
                 # allow_oauth_cache=True
                 )
    first = yt.streams.filter(only_audio=True).first()
    if first is not None:
        downloaded_audio = first.download('./mp3')
        if downloaded_audio == None:
            raise ValueError("Something went wrong")

    # Convert from mp4 to mp3
    music_file_location = default_config["music_file_location"]
    file_path_to_play = None
    currently_playing_name = None
    player.init()
    for file in os.listdir(music_file_location):
        if file.endswith(".mp4"):
            mp4_file = os.path.join(music_file_location, file)
            mp3_file = file[:-4] + ".mp3"
            currently_playing_name = mp3_file
            mp3_file_path = os.path.join(music_file_location, mp3_file)  # Modify file name to change .mp4 to .mp3
            mp4_to_mp3(mp4_file, mp3_file_path)
            os.remove(mp4_file)
            file_path_to_play = mp3_file_path

    window.clear()
    window.refresh()

    # Play music
    player.music.load(file_path_to_play)
    player.music.set_volume(default_config["default_vol"])
    player.music.play()


    thread = threading.Thread(target=listen, args=(window,))
    thread.start()
    # Show progress bar
    window.addstr(0, 0, f"Music playing: {currently_playing_name:<30}", curses.color_pair(1))  # Set color for the line
    window.addstr(3, 0, "[p] Play/Pause        [r] Rewind          [s] Stop                 ",
                  curses.color_pair(3))  # Set color for the line
    window.addstr(4, 0, "[+] Increase Volume   [-] Decrease Volume [q] Quit                 ",
                  curses.color_pair(3))  # Set color for the line

    try:
        while True:
            progress_seconds = player.music.get_pos() / 1000
            progress_minutes = int(progress_seconds // 60)
            progress_seconds_remainder = int(progress_seconds % 60)
            window.addstr(1, 0,
                          f"Progress: {progress_minutes:02d}:{progress_seconds_remainder:02d}  ",
                          curses.color_pair(2))  # Set color for the line

            total_length = 50
            current_progress = int((progress_seconds / total_length) * total_length)
            progress_bar = '[' + '#' * current_progress + '-' * (total_length - current_progress) + ']'
            window.addstr(2, 0, progress_bar)

            window.refresh() # line 165
            time.sleep(1)  # Update every second
    except KeyboardInterrupt:
        # Handle Ctrl+C here
        exit_player(window)



    # Add text
    # search_window.addstr(y - 5, x + 4, "Hello")  # Adjust text position


def mp4_to_mp3(input_file, output_file):
    audio = AudioFileClip(input_file)
    audio.write_audiofile(output_file, verbose=True, logger=None)


def downloaded(window):
    window.addstr(int(curses.LINES /2), int(curses.COLS/2) , "", curses.color_pair(1))



def downloading(window):
    window.addstr(4, 4, "", curses.color_pair(2))
    window.refresh()


def listen(window):
    hotkeys = {
        ord('p'): play_n_pause,
        ord('r'): lambda _=None: player.music.rewind(),  # Modify lambda function
        ord('s'): lambda _=None: player.music.stop(),
        ord('+'): increase_vol,
        ord('-'): decrease_vol,
        ord('q'): exit_player,
        3: exit_player  # Ctrl+C
    }

    curses.start_color()  # Enable color
    curses.use_default_colors()  # Use terminal default colors
    while True:
        key = window.getch()
        if key in hotkeys:
            hotkeys[key](window)


def exit_player(window):
    player.music.stop()
    window.addstr("Stopping music\n")
    window.refresh()
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    os._exit(0)


def play_n_pause(window):
    global player
    if player.music.get_busy():
        player.music.pause()
    else:
        player.music.unpause()


def increase_vol(window):
    global player
    curr_vol = player.music.get_volume()
    if curr_vol > 1:
        curr_vol = 1
    else:
        curr_vol += 0.1
    player.music.set_volume(curr_vol)


def decrease_vol(window):
    global player
    curr_vol = player.music.get_volume()
    if curr_vol < 0:
        curr_vol = 0
    else:
        curr_vol -= 0.1
    player.music.set_volume(curr_vol)


def get_selected_music(window):
    max_y, max_x = window.getmaxyx()

    while True:
        user_input = ""
        enter_text = "Enter text: "
        y_bottom_position = max_y - 2
        window.addstr(y_bottom_position, 2, enter_text, curses.color_pair(3))
        window.move(y_bottom_position, 2 + len(enter_text))

        while True:
            key = window.getch()
            if key == 10:  # Enter key
                break
            elif chr(key).isdigit():
                user_input += chr(key)
                window.addstr(chr(key))
            elif key == 127:  # Backspace key
                if user_input:
                    user_input = user_input[:-1]
                    window.addstr("\b \b")  # Clear the character visually
            window.refresh()

        try:
            number = int(user_input)
            break
        except ValueError:
            window.addstr(y_bottom_position, 2, "Invalid input! Please enter a number.", curses.color_pair(2))
            window.refresh()
            time.sleep(1)
            window.move(y_bottom_position, 2)
            window.clrtoeol()

    return user_input
