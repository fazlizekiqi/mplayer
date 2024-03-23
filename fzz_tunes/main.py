import io
import os
import tempfile
import time
from .search_youtube import SearchYoutube
from pytube import YouTube
from pygame import mixer
from moviepy.editor import AudioFileClip
import threading
from .os_compatibility import curses
from .configs import default_config, init_curses_colors
from .windows import WindowManager

player = mixer
music_is_playing = False
current_state = None


class State:
    GET_USER_INPUT = 1
    GET_SELECTED_MUSIC = 2
    ADD_LOADING_MESSAGE = 3
    PLAY_MUSIC = 4


def add_screen(stdscr):
    global current_state
    init_curses_colors()
    manager = WindowManager()

    current_state = State.GET_USER_INPUT
    input_search = None
    selected_music_index = None
    results = None

    try:
        while True:
            if current_state == State.GET_USER_INPUT:
                input_search = get_user_search(manager)
                current_state = State.GET_SELECTED_MUSIC
            elif current_state == State.GET_SELECTED_MUSIC:
                results, selected_music_index = get_selected_music(input_search, manager)
                current_state = State.ADD_LOADING_MESSAGE
            elif current_state == State.ADD_LOADING_MESSAGE:
                manager.add_loading_message()
                current_state = State.PLAY_MUSIC
            elif current_state == State.PLAY_MUSIC:
                play_music(manager, results[selected_music_index - 1])
    except ValueError as e:
        print(e)
        time.sleep(3)
        exit_player()


def play_music(manager, selected_music):
    global current_state, music_is_playing
    download_and_convert_audio(selected_music)
    manager.clear()
    manager.refresh()

    file_path = os.path.join(default_config["music_file_location"], selected_music.title + ".mp3")
    player.music.load(file_path)
    player.music.set_volume(default_config["default_vol"])

    player.music.play()  # Set -1 to repeat the music

    music_is_playing = True
    thread = threading.Thread(target=listen, args=(manager,))
    thread.start()

    while music_is_playing:
        manager.add_music_details(selected_music.title)
        manager.add_music_player_instructions()
        music_length = selected_music.duration

        if player.music.get_busy():
            progress_seconds = player.music.get_pos() / 1000
            progress_minutes = int(progress_seconds // 60)
            seconds_left = int(progress_seconds % 60)
            manager.progress_bar(progress_seconds, progress_minutes, seconds_left, music_length)

        manager.refresh()
        time.sleep(1)

    else:
        manager.clear()
        manager.refresh()


def download_and_convert_audio(selected_music):
    yt = YouTube(selected_music.link)
    audio_stream = yt.streams.filter(only_audio=True).first()

    if audio_stream:

        audio_buffer = io.BytesIO()
        audio_stream.stream_to_buffer(audio_buffer)
        audio_buffer.seek(0)

        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_filename = temp_file.name
            temp_file.write(audio_buffer.getvalue())

        filename = selected_music.title + ".mp3"
        file = os.path.join(default_config["music_file_location"], filename)
        audio_clip = AudioFileClip(temp_filename)

        if not os.path.exists(file):
            audio_clip.write_audiofile(file, verbose=True, logger=None)

    else:
        raise ValueError("No audio stream found!")


def get_selected_music(input_search, manager):
    search_youtube = SearchYoutube()
    results = search_youtube.search(input_search)
    manager.render_list_items(results)
    while True:
        user_input = ""
        manager.add_select_music_field()

        while True:
            key = manager.getch()
            if key == 10:  # Enter key
                break
            elif chr(key).isdigit():
                user_input += chr(key)
                manager.addstr(chr(key))
            elif key == 127:  # Backspace key
                if user_input:
                    user_input = user_input[:-1]
                    manager.addstr("\b \b")  # Clear the character visually
            manager.refresh()

        try:
            number = int(user_input)
            break
        except ValueError:
            manager.add_error_message()
    selected_music_index = int(user_input)
    return results, selected_music_index


def get_user_search(manager):
    manager.add_author()
    manager.add_banner()
    manager.add_search_box()
    manager.refresh()
    input_search = manager.get_user_search()
    manager.clear()
    manager.add_border()
    manager.refresh()
    return input_search


def mp4_to_mp3(input_file, output_file):
    audio = AudioFileClip(input_file)
    audio.write_audiofile(output_file, verbose=True, logger=None)


def listen(window_manager):
    global music_is_playing
    curses.start_color()  # Enable color
    curses.use_default_colors()  # Use terminal default colors

    while music_is_playing:
        key = window_manager.getch()

        if key == ord('p'):
            play_n_pause()
        elif key == ord('r'):
            rewind(window_manager)
        elif key == ord('s'):
            search_music()
        elif key == ord('b'):
            select_music()
        elif key == ord('+'):
            increase_vol()
        elif key == ord('-'):
            decrease_vol()
        elif key == ord('q') or key == 3:  # Ctrl+C
            exit_player()


def stop_music():
    global music_is_playing, current_state
    music_is_playing = False
    current_state = State.GET_SELECTED_MUSIC
    player.music.stop()


def select_music():
    global music_is_playing, current_state
    music_is_playing = False
    current_state = State.GET_SELECTED_MUSIC
    player.music.stop()


def search_music():
    global music_is_playing, current_state
    music_is_playing = False
    current_state = State.GET_USER_INPUT
    player.music.stop()


def exit_player():
    global music_is_playing
    music_is_playing = False
    player.music.stop()
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    os._exit(0)


def play_n_pause():
    global player
    if player.music.get_busy():
        player.music.pause()
    else:
        player.music.unpause()


def rewind(window_manager):
    player.music.rewind()
    player.music.play(0, 00)



def increase_vol():
    global player
    curr_vol = player.music.get_volume()
    if curr_vol > 1:
        curr_vol = 1
    else:
        curr_vol += 0.1
    player.music.set_volume(curr_vol)


def decrease_vol():
    global player
    curr_vol = player.music.get_volume()
    if curr_vol < 0:
        curr_vol = 0
    else:
        curr_vol -= 0.1
    player.music.set_volume(curr_vol)


def main():
    import ssl
    ssl._create_default_https_context = ssl._create_stdlib_context

    location_ = default_config['music_file_location']
    for file in os.listdir(location_):
        file_path = os.path.join(location_, file)
        os.remove(file_path)
    curses.wrapper(add_screen)
