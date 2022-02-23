from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Generator, List

import PySimpleGUI as sg  # type: ignore

import add_songs
import utils
from player.audio_player import AudioPlayer
from player.playlist import SUPPORTED_AUDIO_FILES, PlaylistItem

WINDOW_TIMEOUT = 10


class CustomTable(sg.Table):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.RowHeaderText = "#"


class MousaiGUI:
    PLAY_BTN_SYMBOL = "▶"
    PAUSE_BTN_SYMBOL = "| |"

    audio_file_types = (("Supported audio file", " ".join(SUPPORTED_AUDIO_FILES)),)

    menu_layout = [
        [
            "File",
            [
                "Add songs",
                "---",
                "Show queue",
                "---",
                "!Save playlist",
                "!Load playlist",
                "---",
                "&Exit",
            ],
        ],
        ["Edit", ["!Settings"]],
        ["Help", "!About"],
    ]

    def __init__(self, theme: str = "DarkAmber") -> None:
        self._default_art_cover = utils.get_default_art_cover()
        self.theme = theme
        self.player = AudioPlayer()
        add_songs.add_songs(self.player.playlist)
        self.layout = self.create_layout()
        self.window = sg.Window("Mousai", self.layout, resizable=False, finalize=True)

        # Keyboard shortcuts
        # 'RETURN': Start selected song from playlist
        # 'N': Decrease volume
        # 'M': Increase volume
        # 'SPACE': Pause/Resume current song
        # 'R': Restart current song

        self.window["-TABLE-"].bind("<Return>", "+START_KEY_PRESS+")
        self.window.bind("n", "+N_KEY_PRESS+")
        self.window.bind("m", "+M_KEY_PRESS+")
        self.window.bind("<space>", "+SPACE_KEY_PRESS+")
        self.window.bind("r", "+R_KEY_PRESS+")

    def get_song_art(self, song_meta_art: BytesIO | None) -> bytes:
        """Returns song art cover to display in `Metadata` frame;
        If its not present in audio file metadata return default one."""
        if not song_meta_art:
            return self._default_art_cover

        return utils.resize_img(song_meta_art)

    def set_current_song(self, song: PlaylistItem) -> None:
        if self.player.current_song is None:
            # this runs when first song since launching the app is picked by user to be played
            self.player.init_queue()
        else:
            self.player.add_to_history(self.player.current_song)

        self.window["-PLAY_PAUSE_BTN-"].update(self.PAUSE_BTN_SYMBOL)
        self.player.stop()
        self.player.current_song = song

        self.set_metadata_frame()
        self.set_timers()

        self.player.play()

        # Because when new music is loaded the volume is set to full volume
        self.player.set_volume(self.player.volume)

    def create_layout(self) -> List[List[sg.Pane]]:
        right_col = [
            [
                CustomTable(
                    values=self.playlist_to_table(),
                    headings=["Track", "Artist", "Duration"],
                    col_widths=[19, 15, 7],
                    max_col_width=15,
                    auto_size_columns=False,
                    display_row_numbers=True,
                    justification="left",
                    expand_y=True,
                    enable_events=True,
                    enable_click_events=True,
                    key="-TABLE-",
                )
            ]
        ]
        controls = [
            sg.Button("<<", key="-RESTART_SONG_BTN-"),
            sg.Button(self.PLAY_BTN_SYMBOL, focus=True, key="-PLAY_PAUSE_BTN-"),
            sg.Button(">>", key="-NEXT_SONG_BTN-"),
        ]

        left_col = [
            [
                sg.Frame(
                    "Playing",
                    [
                        [
                            sg.Image(
                                self._default_art_cover,
                                size=(256, 256),
                                key="-META_IMG-",
                            ),
                            sg.Column(
                                [
                                    [sg.Text("", size=16, key="-META_TITLE-")],
                                    [sg.Text("", size=16, key="-META_ALBUM-")],
                                    [sg.Text("", size=16, key="-META_ARTIST-")],
                                    [sg.Text("", size=16, key="-META_DATE-")],
                                ],
                            ),
                        ],
                    ],
                    expand_y=True,
                )
            ]
        ]

        layout = [
            [sg.Menu(self.menu_layout)],
            [
                sg.Column(left_col, expand_y=True),
                sg.Column(right_col, expand_y=True),
            ],
            [
                sg.Text("-:--", key="-PLAY_TIME-"),
                sg.ProgressBar(
                    max_value=1000,
                    orientation="h",
                    size_px=(1, 5),
                    expand_x=True,
                    key="-PROG_BAR-",
                ),
                sg.Text("-:--", key="-PLAY_DURATION-"),
            ],
            [
                sg.Button("Random", disabled=True),
                sg.Button("Loop", disabled=True),
                sg.Push(),
                *controls,
                sg.Push(),
                sg.Text(
                    int(self.player.volume * 100),
                    size=3,
                    justification="center",
                    key="-VOLUME_TEXT-",
                ),
                sg.Slider(
                    range=(0, 100),
                    default_value=self.player.volume * 100,
                    orientation="horizontal",
                    size=(12, 14),
                    enable_events=True,
                    disable_number_display=True,
                    key="-VOLUME_SLIDER-",
                ),
            ],
        ]

        return layout

    def get_audio_file_path(self) -> None | Generator[Path, None, None]:
        paths = sg.popup_get_file(
            "Please enter audio file path",
            multiple_files=True,
            no_window=True,
            keep_on_top=True,
            file_types=MousaiGUI.audio_file_types,
        )

        if paths is None or len(paths) < 1:
            return None

        paths_gen = (Path(path) for path in paths if path)

        return paths_gen

    def playlist_to_table(self) -> List[List[str]]:
        """Creates list of lists which contain values for playlist table in [Title, Artist, Duration] format"""
        table_data = []
        for song in self.player.playlist:
            title = song.meta.title if song.meta.title else song.meta.file_name
            artist = song.meta.artist if song.meta.artist else "-"
            duration = "-"

            if song.meta.playtime:
                duration = utils.playtime_to_str(song.meta.playtime)

            table_data.append([title, artist, duration])

        return table_data

    def set_metadata_frame(self) -> None:
        song = self.player.current_song

        if song:
            song_title = song.meta.title

            if song_title is None:
                song_title = song.meta.file_name

            data = {
                "-META_TITLE-": song_title,
                "-META_ALBUM-": song.meta.album,
                "-META_ARTIST-": song.meta.artist,
                "-META_DATE-": song.meta.release_date,
                "-META_IMG-": self.get_song_art(song.meta.art),
            }

            for k, v in data.items():
                if isinstance(v, bytes):
                    self.window[k].update(
                        v, size=(256, 256)
                    )  # updating size too bcs the image could be not a square and that would cause whole window to resize
                else:
                    self.window[k].update(v if v else "-")
                    self.window[k].set_tooltip(v)

    # def update_progress_bar(self) -> None:
    #     return NotImplementedError

    def set_timers(self, start="0:00") -> None:
        end = "-:--"
        if self.player.current_song:
            end = utils.playtime_to_str(self.player.current_song.meta.playtime)
        self.window["-PLAY_TIME-"].update(start)
        self.window["-PLAY_DURATION-"].update(end)

    def restart_current_song(self) -> None:
        if self.player.current_song:
            if self.player.playback_paused:
                self.player.play()
            self.set_current_song(self.player.current_song)

    def handle_volume_change(self, value: float) -> None:
        if value > 100:
            value = 100
        elif value < 0:
            value = 0
        self.player.set_volume(value / 100)
        self.window["-VOLUME_TEXT-"].update(f"{value:0.0f}")
        self.window["-VOLUME_SLIDER-"].update(value)

    def run(self) -> None:
        while True:
            event, values = self.window.read(timeout=WINDOW_TIMEOUT)  # type: ignore
            if event != "__TIMEOUT__":
                print(f"{event=} {values=}")

            # There is current song set and is not paused
            if self.player.current_song and not self.player.playback_paused:
                current_playtime = self.player.get_playtime()

                # Song ended
                if current_playtime == -1:
                    # Get next song from queue and play it
                    self.set_current_song(self.player.get_next_song())
                # Song playing
                else:
                    current_playtime_in_seconds = round(current_playtime / 1000)

                    # Update play time and progress bar
                    self.window["-PLAY_TIME-"].update(
                        utils.playtime_to_str(current_playtime_in_seconds)
                    )
                    self.window["-PROG_BAR-"].update(
                        current_playtime_in_seconds,
                        self.player.current_song.meta.playtime,
                    )

            # TABLE CLICKED Event has value in format ('.TABLE', '+CLICKED+', (row, col))
            if isinstance(event, tuple):
                # Item in table was clicked
                if event[0] == "-TABLE-":
                    print(f"{event=} {values=}")
                    value = event[2][0]
                    if value is not None:  # can be None if user clicks on table headers
                        self.set_current_song(self.player.playlist[value])
            else:
                # MENU EVENTS

                # Menu -> File -> Exit or window closed
                if event == "Exit" or event == sg.WINDOW_CLOSED:
                    break

                # Menu -> File -> Add song
                elif event == "Add songs":
                    paths = self.get_audio_file_path()

                    if paths:
                        added_songs_count = 0
                        for song_path in paths:
                            try:
                                self.player.playlist.add(
                                    PlaylistItem.from_file(song_path)
                                )
                            except ValueError as e:
                                sg.popup_error(
                                    "Error", e, non_blocking=True, keep_on_top=True
                                )
                            else:
                                added_songs_count += 1

                        if added_songs_count > 0:
                            sg.popup_ok(
                                f"{added_songs_count} song{'s' if added_songs_count > 1 else ''} added to playlist",
                                title="Success",
                                non_blocking=True,
                                keep_on_top=True,
                            )

                            self.window["-TABLE-"].update(
                                values=self.playlist_to_table()
                            )

                # Menu -> File -> Show queue
                elif event == "Show queue":
                    queue_items = self.player.get_queue_items()
                    msg = "\n".join(
                        f"{i}. {str(song)}"
                        for i, song in enumerate(queue_items, start=1)
                    )
                    sg.popup_ok(msg, title="Queue", non_blocking=True)

                # BUTTONS/SLIDERS

                # Volume slider moved
                elif event == "-VOLUME_SLIDER-":
                    value = values["-VOLUME_SLIDER-"]
                    self.handle_volume_change(value)

                # Play/Pause btn clicked or spacebar pressed
                elif event == "-PLAY_PAUSE_BTN-" or event == "+SPACE_KEY_PRESS+":
                    if self.player.current_song:

                        # Start playing if player was paused or pause if otherwise
                        if self.player.playback_paused:
                            self.player.play()
                            self.window["-PLAY_PAUSE_BTN-"].update(
                                self.PAUSE_BTN_SYMBOL
                            )
                        else:
                            self.player.pause()
                            self.window["-PLAY_PAUSE_BTN-"].update(self.PLAY_BTN_SYMBOL)
                elif event == "-RESTART_SONG_BTN-":
                    self.restart_current_song()
                # Next Song btn clicked
                elif event == "-NEXT_SONG_BTN-":
                    if self.player.playback_paused:
                        self.player.play()
                    self.set_current_song(self.player.get_next_song())

                # KEYBOARD SHORTCUTS

                # Keyboard shortcut to change volume
                elif event == "+N_KEY_PRESS+" or event == "+M_KEY_PRESS+":
                    step = 5 if event[1] == "M" else -5
                    new_v = self.player.volume * 100 + step

                    self.handle_volume_change(new_v)

                # Return key pressed on table item
                elif event == "-TABLE-+START_KEY_PRESS+":
                    value = values["-TABLE-"][0]
                    self.set_current_song(self.player.playlist[value])

                # 'R' key pressed
                elif event == "+R_KEY_PRESS+":
                    self.restart_current_song()

        # Cleanup before exit
        if self.player.is_playing:
            self.player.stop()

        self.player.clean_up()
        self.window.close()


if __name__ == "__main__":
    app = MousaiGUI()
    app.run()
