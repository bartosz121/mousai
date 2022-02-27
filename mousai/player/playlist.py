import io
import random
import reprlib
from datetime import datetime
from pathlib import Path
from typing import Iterator, List, NamedTuple, Optional

import eyed3  # type: ignore

# TODO ANNOTATIONS


SUPPORTED_AUDIO_FILES = (".mp3", ".ogg", ".wav")


class AudioMetaData(NamedTuple):
    file_name: str
    playtime: float = 0
    artist: Optional[str] = None
    album: Optional[str] = None
    title: Optional[str] = None
    genre: Optional[str] = None
    release_date: Optional[datetime] = None
    art: Optional[io.BytesIO] = None

    @classmethod
    def from_file(cls, path: Path) -> "AudioMetaData":
        try:
            audiofile = eyed3.load(path)
        except OSError:
            raise FileNotFoundError(f"File not found: {path!r}")
        else:
            if audiofile is None or audiofile.tag is None:
                return cls(path.resolve().parts[-1])

        # Check for art cover
        art = None
        if len(audiofile.tag.images) > 0:
            art = io.BytesIO(audiofile.tag.images[0].image_data)

        return cls(
            path.name,
            audiofile.info.time_secs,  # type: ignore
            audiofile.tag.artist,
            audiofile.tag.album,
            audiofile.tag.title,
            audiofile.tag.genre,
            audiofile.tag.getBestDate(),
            art,
        )


class PlaylistItem:
    def __init__(self, path, meta_data) -> None:
        self.path: Path = path
        self.meta: AudioMetaData = meta_data
        self.added = datetime.utcnow()

    def __repr__(self) -> str:
        return f"PlaylistItem.from_file({self.path})"

    def __str__(self) -> str:
        if self.meta.title is None or self.meta.artist is None:
            return self.meta.file_name
        return f"{self.meta.title} - {self.meta.artist}"

    def _get_metadata(self, song: str) -> str:
        raise NotImplementedError

    @classmethod
    def from_file(cls, path: Path) -> "PlaylistItem":
        if not path.exists():
            raise ValueError("File does not exist")

        if path.suffix not in SUPPORTED_AUDIO_FILES:
            raise ValueError(f"{path.suffix!r} files are not supported")

        meta_data = AudioMetaData.from_file(path)

        return cls(path, meta_data)


class Playlist:
    def __init__(self, songs: List[PlaylistItem] = None) -> None:
        if songs is None:
            songs = []
        self.songs: List[PlaylistItem] = songs

    def __repr__(self) -> str:
        items = reprlib.repr(self.songs)
        return f"Playlist({items})"

    def __str__(self) -> str:
        return f"Playlist_({len(self.songs)})_items"

    def __iter__(self) -> Iterator[PlaylistItem]:
        return iter(self.songs)

    def __getitem__(self, key) -> PlaylistItem:
        return self.songs[key]

    def __setitem__(self, key, value: PlaylistItem) -> None:
        self.songs[key] = value

    def __len__(self):
        return self.songs.__len__()

    def add(self, item: PlaylistItem) -> None:
        self.songs.append(item)

    def remove(self, item_index) -> None:
        del self.songs[item_index]

    def get_random_item(self) -> PlaylistItem:
        if len(self.songs) < 1:
            raise PlayerError("No items in playlist.")

        return random.choice(self.songs)

    def remove_duplicates(self, item) -> None:
        raise NotImplementedError


class PlayerError(Exception):
    pass
