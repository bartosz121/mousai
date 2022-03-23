from mousai.player.playlist import AudioMetaData, PlaylistItem

from conftest import TEST_FILE_PATH


def test_from_file(test_file: PlaylistItem):
    assert test_file.path == TEST_FILE_PATH


def test_str(test_file: PlaylistItem):
    assert str(test_file) == "15 Seconds of Silence - Anar Software LLC"


def test_str_meta_title_artist_is_none():
    dummy_meta_data = AudioMetaData("test.mp3")
    item = PlaylistItem(__file__, meta_data=dummy_meta_data)

    assert str(item) == "test.mp3"
