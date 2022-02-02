import io
import reprlib
from datetime import datetime
from pathlib import Path
from typing import Iterator, List, NamedTuple, Optional

import eyed3  # type: ignore
from pydub import AudioSegment  # type: ignore

# TODO ANNOTATIONS


class AudioMetaData(NamedTuple):
    file_name: str
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
            audiofile.tag.file_info.name,
            audiofile.tag.artist,
            audiofile.tag.album,
            audiofile.tag.title,
            audiofile.tag.genre,
            audiofile.tag.getBestDate(),
            art,
        )


class PlaylistItem:
    def __init__(self, path, audio, meta_data) -> None:
        self.path: Path = path
        self.audio: AudioSegment = audio
        self.audio_readonly: AudioSegment = audio
        self.duration: int = len(audio)
        self.meta = meta_data
        self.added = datetime.utcnow()

    def __repr__(self) -> str:
        return f"PlaylistItem.from_file({self.path})"

    def __str__(self) -> str:
        return f"PlaylistItem_{self.meta.title}_by_{self.meta.artist}"

    def _get_metadata(self, song: str) -> str:
        raise NotImplementedError

    @classmethod
    def from_file(cls, path: Path) -> "PlaylistItem":
        try:
            audio = AudioSegment.from_file(path)
            meta_data = AudioMetaData.from_file(path)
        except FileNotFoundError as e:
            raise e

        return cls(path, audio, meta_data)


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

    def add(self, item: PlaylistItem) -> None:
        self.songs.append(item)

    def remove(self, item_index) -> None:
        del self.songs[item_index]

    def remove_duplicates(self, item) -> None:
        raise NotImplementedError
