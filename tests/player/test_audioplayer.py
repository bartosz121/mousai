import pytest
from mousai.player.audio_player import AudioPlayer
from mousai.player.playlist import PlaylistItem


@pytest.fixture
def audioplayer(dummy_playlist_with_items) -> AudioPlayer:
    ap = AudioPlayer()
    ap.playlist = dummy_playlist_with_items
    ap.init_queue()

    return ap


def test_add_to_history(audioplayer: AudioPlayer, test_file: PlaylistItem):
    ap = audioplayer
    item = test_file

    ap.add_to_history(item)
    assert ap._history[-1] is item

    # Do not add same item to history if it was played two or more times in a row
    ap.add_to_history(item)
    assert len(ap._history) == 1


def test_add_to_queue(audioplayer: AudioPlayer, test_file: PlaylistItem):
    ap = audioplayer
    item = test_file

    ap.add_to_queue(item)
    assert ap._queue[-1] is item

    ap.add_to_queue(item, next=True)
    assert ap._queue[0] is item


def test_get_playlistitems_gen(audioplayer: AudioPlayer, test_file: PlaylistItem):
    ap = audioplayer
    queue_gen = ap.get_playlistitems_gen(source="queue")

    assert all([a == b for a, b in zip(ap._queue, queue_gen)])

    for _ in range(10):
        ap.add_to_history(test_file)

    history_gen = ap.get_playlistitems_gen(source="history")
    assert all([a == b for a, b in zip(ap._history, history_gen)])


def test_get_next_song(audioplayer: AudioPlayer):
    ap = audioplayer

    last_item = ap._queue[0]

    assert last_item is ap.get_next_song()
