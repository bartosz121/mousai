from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import List

import PySimpleGUI as sg  # type: ignore

import add_songs
import utils
from player.audio_player import AudioPlayer
from player.playlist import PlaylistItem

WINDOW_TIMEOUT = 10


class CustomTable(sg.Table):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.RowHeaderText = "#"


class MousaiGUI:
    audio_file_types = (("Supported audio file", ".mp3 .ogg .wav"),)

    def __init__(self, theme: str = "DarkAmber") -> None:
        self._default_art_cover = utils.get_default_art_cover()
        self.theme = theme
        self.player = AudioPlayer()
        add_songs.add_songs(self.player.playlist)
        self.gui_playtime = 0.00
        self.layout = self.create_layout()
        self.window = sg.Window("Mousai", self.layout, resizable=False, finalize=True)

        # Keyboard shortcuts
        self.window["-TABLE-"].bind("<Return>", "+START_KEY_PRESS+")
        self.window.bind("<space>", "+SPACE_KEY_PRESS+")
        self.window.bind("r", "+R_KEY_PRESS+")

    def get_song_art(self, song_meta_art: BytesIO | None) -> bytes:
        """Returns song art cover to display in `Metadata` frame;
        If its not present in audio file metadata return default one."""
        if not song_meta_art:
            return self._default_art_cover

        return utils.resize_img(song_meta_art)

    def set_current_song(self, song: PlaylistItem) -> None:
        self.player.stop()
        self.player.current_song = song
        self.set_metadata_frame()
        self.set_timers()
        self.player.play()

    def create_layout(self) -> List[List[sg.Pane]]:
        right_col = [
            [
                CustomTable(
                    values=self.playlist_to_table(),
                    headings=["Track", "Artist", "Duration"],
                    max_col_width=18,
                    auto_size_columns=True,
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
            sg.Button("Random", disabled=True),
            sg.Button("<<", disabled=True),
            sg.Button("▶", focus=True, key="-PLAY_PAUSE_BTN-"),
            sg.Button(">>", disabled=True),
            sg.Button("Loop", disabled=True),
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
            [sg.Push(), *controls, sg.Push()],
        ]

        return layout

    # def import_audio_file(self) -> None:
    #     file = sg.popup_get_file(
    #         "Please enter a file name",
    #         multiple_files=True,
    #         file_types=MousaiGUI.audio_file_types,
    #     )
    #     print(file)

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

    def run(self) -> None:
        while True:
            event, values = self.window.read(timeout=WINDOW_TIMEOUT)  # type: ignore
            if event != "__TIMEOUT__":
                print(f"{event=} {values=}")
            # print(repr(self.player.playlist))

            if self.player.current_song and not self.player.playback_paused:
                current_playtime = round(self.player.get_playtime() / 1000)

                self.window["-PLAY_TIME-"].update(
                    utils.playtime_to_str(current_playtime)
                )
                self.window["-PROG_BAR-"].update(
                    current_playtime, self.player.current_song.meta.playtime
                )
            if isinstance(event, tuple):
                # TABLE CLICKED Event has value in format ('.TABLE', '+CLICKED+', (row,col))
                if event[0] == "-TABLE-":
                    print(f"{event=} {values=}")
                    value = event[2][0]
                    if value is not None:  # can be None if user clicks on table headers
                        self.set_current_song(self.player.playlist[value])
            else:
                if event == sg.WINDOW_CLOSED:
                    break

                elif event == "-PLAY_PAUSE_BTN-" or event == "+SPACE_KEY_PRESS+":
                    if self.player.current_song:
                        if self.player.playback_paused:
                            self.player.play()
                        else:
                            self.player.pause()

                elif event == "-TABLE-+START_KEY_PRESS+":
                    value = values["-TABLE-"][0]
                    self.set_current_song(self.player.playlist[value])

                elif event == "+R_KEY_PRESS+":
                    if self.player.current_song:
                        self.set_current_song(self.player.current_song)

        if self.player.is_playing:
            self.player.stop()

        self.player.clean_up()
        self.window.close()


if __name__ == "__main__":
    app = MousaiGUI()
    app.run()
