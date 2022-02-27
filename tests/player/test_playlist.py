def test_init_with_songs(dummy_playlist_with_items, test_file):
    playlist = dummy_playlist_with_items

    assert playlist.songs == [test_file for _ in range(10)]


def test_add(dummy_playlist_with_items, test_file):
    playlist = dummy_playlist_with_items
    new_item = test_file

    playlist.add(test_file)

    assert playlist.songs[-1] is new_item


def test_remove(dummy_playlist_with_items, test_file):
    playlist = dummy_playlist_with_items
    length = len(playlist.songs)

    playlist.remove(1)

    assert len(playlist.songs) == length - 1
