from pathlib import Path

import pytest
from mousai.player.playlist import AudioMetaData

from conftest import TEST_FILE_PATH

TEST_FILE_ART_DATA = ""


def test_from_file():
    item = AudioMetaData.from_file(TEST_FILE_PATH)

    assert item.file_name == "15-seconds-of-silence.mp3"
    assert item.artist == "Anar Software LLC"
    assert item.album == "Blank Audio"
    assert item.title == "15 Seconds of Silence"
    assert item.genre == "Blank Audio Genre"
    assert item.playtime == pytest.approx(15.3, abs=1e-1)
    assert str(item.release_date) == "2015"
    assert item.art is not None


def test_from_file_filenotfound():
    bad_path = Path(__file__) / "filenotfound.mp3"

    with pytest.raises(FileNotFoundError):
        AudioMetaData.from_file(bad_path)
