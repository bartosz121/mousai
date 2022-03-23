def test_init_with_songs(dummy_playlist_with_items, test_file):
    assert dummy_playlist_with_items.songs == [test_file for _ in range(10)]


def test_add(dummy_playlist_with_items, test_file):
    new_item = test_file

    dummy_playlist_with_items.add(test_file)

    assert dummy_playlist_with_items.songs[-1] is new_item


def test_remove(dummy_playlist_with_items, test_file):
    length = len(dummy_playlist_with_items.songs)

    dummy_playlist_with_items.remove(1)

    assert len(dummy_playlist_with_items.songs) == length - 1
