from __future__ import annotations

from collections import deque

from pygame import mixer

from .playlist import Playlist, PlaylistItem


class AudioPlayer:
    def __init__(self) -> None:
        mixer.init()
        self.playlist = Playlist()
        self.current_song: PlaylistItem | None = None
        self._queue = deque(maxlen=10)  # TODO annotate this
        self._history = deque()
        self.playback_paused = False

    def add_to_history(self, item) -> None:  # TODO annotate item
        self._history.appendleft(item)

    def add_to_queue(self, item: str | None = None) -> None:  # TODO annotate item
        """
        Adds item to queue.

        If item is STR(TODO) its appended to the left - to be played right after current song;

        else - get random song from playlist and append it to the right
        """
        if item is None:
            # TODO grab random song from playlist
            # item = self._get_random_song()
            self._queue.append(item)
            pass
        # if item is not None (can only happen when user wants to play this song after current one)
        # append to the start
        self._queue.appendleft(item)

    def is_playing(self) -> bool:
        """Is there any audio currently playing"""
        return mixer.music.get_busy()

    def set_playtime(self, value: float) -> None:
        mixer.music.set_pos(value)

    def get_playtime(self) -> float:
        return mixer.music.get_pos()

    def play(self) -> None:
        if self.current_song:
            if self.playback_paused:
                mixer.music.unpause()
            else:
                mixer.music.stop()
                mixer.music.load(self.current_song.path)  # TODO opitmization???
                mixer.music.play()

            self.playback_paused = False
        else:
            raise ValueError(f"Current song is not set. {self.current_song=!r}")

    def stop(self) -> None:
        """Stop any playback"""
        mixer.music.stop()
        mixer.music.unload()

    def pause(self) -> None:
        mixer.music.pause()
        self.playback_paused = True

    def clean_up(self) -> None:
        """Unload the currently loaded music to free up resources"""
        mixer.music.unload()
