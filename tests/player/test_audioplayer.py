import pytest
from mousai.player.audio_player import AudioPlayer
from mousai.player.playlist import PlaylistItem


def test_add_to_history(audioplayer: AudioPlayer, test_file: PlaylistItem):
    audioplayer.add_to_history(test_file)
    assert audioplayer._history[-1] is test_file

    # Do not add same item to history if it was played two or more times in a row
    audioplayer.add_to_history(test_file)
    assert len(audioplayer._history) == 1


def test_add_to_queue(audioplayer: AudioPlayer, test_file: PlaylistItem):
    audioplayer.add_to_queue(test_file)
    assert audioplayer._queue[-1] is test_file

    audioplayer.add_to_queue(test_file, next=True)
    assert audioplayer._queue[0] is test_file


def test_get_playlistitems_gen(audioplayer: AudioPlayer, test_file: PlaylistItem):
    queue_gen = audioplayer.get_playlistitems_gen(source="queue")

    assert all([a == b for a, b in zip(audioplayer._queue, queue_gen)])

    for _ in range(10):
        audioplayer.add_to_history(test_file)

    history_gen = audioplayer.get_playlistitems_gen(source="history")
    assert all([a == b for a, b in zip(audioplayer._history, history_gen)])


def test_get_next_song(audioplayer: AudioPlayer):
    last_item = audioplayer._queue[0]

    assert last_item is audioplayer.get_next_song()
