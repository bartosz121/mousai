from .playlist import (
    PlayerError as PlayerError,
    Playlist as Playlist,
    PlaylistItem as PlaylistItem,
)
from typing import Any, Generator

class AudioPlayer:
    QUEUE_MAX_LEN: int
    HISTORY_MAX_LEN: int
    playlist: Any
    current_song: Any
    volume: float
    playback_paused: bool
    def __init__(self) -> None: ...
    def init_queue(self) -> None: ...
    def add_to_history(self, item: PlaylistItem) -> None: ...
    def add_to_queue(self, item: PlaylistItem = ..., next: bool = ...) -> None: ...
    def get_playlistitems_gen(
        self, source: str
    ) -> Generator[PlaylistItem, None, None]: ...
    def get_next_song(self) -> PlaylistItem: ...
    def is_playing(self) -> bool: ...
    def set_playtime(self, value: float) -> None: ...
    def get_playtime(self) -> float: ...
    def set_volume(self, value: float) -> None: ...
    def play(self) -> None: ...
    def stop(self) -> None: ...
    def pause(self) -> None: ...
    def clean_up(self) -> None: ...
