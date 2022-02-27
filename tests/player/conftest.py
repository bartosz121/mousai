from pathlib import Path

import pytest
from mousai.player.playlist import Playlist, PlaylistItem

# using 15 seconds of silence as test audio file from https://github.com/anars/blank-audio
TEST_FILE_PATH = Path(__file__).parent / "15-seconds-of-silence.mp3"


@pytest.fixture
def test_file() -> PlaylistItem:
    return PlaylistItem.from_file(TEST_FILE_PATH)


@pytest.fixture
def dummy_playlist_with_items(test_file):
    """Returns `Playlist` with 10 items"""
    return Playlist(songs=[test_file for _ in range(10)])
