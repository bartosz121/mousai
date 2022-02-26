from __future__ import annotations

from collections import deque
from typing import Deque, Generator

from pygame import mixer

from .playlist import PlayerError, Playlist, PlaylistItem


class AudioPlayer:
    QUEUE_MAX_LEN = 10
    HISTORY_MAX_LEN = 10

    def __init__(self) -> None:
        mixer.init()
        self.playlist = Playlist()
        self.current_song: PlaylistItem | None = None
        self.volume = 0.05
        self._queue: Deque[PlaylistItem] = deque(maxlen=self.QUEUE_MAX_LEN)
        self._history: Deque[PlaylistItem] = deque(maxlen=self.HISTORY_MAX_LEN)
        self.playback_paused = False

        mixer.music.set_volume(self.volume)

    def init_queue(self) -> None:
        """
        This method is meant to be ran when you want to populate queue for first time.
        """
        for _ in range(self.QUEUE_MAX_LEN):
            self.add_to_queue()

    def add_to_history(self, item: PlaylistItem) -> None:
        """
        Adds item to `self._history`;
        also checks if last item in history is equal to argument `item`
        if yes - dont add it
        """
        try:
            last = self._history[0]
        except IndexError:
            self._history.appendleft(item)
        else:
            if item != last:
                self._history.appendleft(item)

    def add_to_queue(self, item: PlaylistItem = None, next: bool = False) -> None:
        """
        Adds item to queue.

        If item is None pick random song from playlist.

        If `next` is True, item is appended to the left - to be played right after current song;
        """
        if item is None:
            try:
                item = self.playlist.get_random_item()
            except PlayerError:
                raise

        if next:
            self._queue.appendleft(item)
        else:
            self._queue.append(item)

    def get_playlistitems_gen(
        self, *, source: str
    ) -> Generator[PlaylistItem, None, None]:
        """
        Returns generator with items from `_queue` or `_history` attributes.
        Raises `ValueError` if not allowed source is passed
        """
        if source == "queue":
            src = iter(self._queue)
        elif source == "history":
            src = iter(self._history)
        else:
            raise ValueError(f"Cant fetch items from {source!r}. See docstring")

        return (song for song in src)

    def get_next_song(self) -> PlaylistItem:
        next_song = self._queue.popleft()
        self.add_to_queue()  # add new song to the end of the queue
        return next_song

    def is_playing(self) -> bool:
        """Is there any audio currently playing"""
        return mixer.music.get_busy()

    def set_playtime(self, value: float) -> None:
        mixer.music.set_pos(value)

    def get_playtime(self) -> float:
        return mixer.music.get_pos()

    def set_volume(self, value: float) -> None:
        self.volume = round(value, 2)
        mixer.music.set_volume(self.volume)

    def play(self) -> None:
        if self.current_song:
            if self.playback_paused:
                mixer.music.unpause()
            else:
                mixer.music.stop()
                mixer.music.load(self.current_song.path)
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
