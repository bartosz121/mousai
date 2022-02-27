from mousai import utils


def test_playtime_to_str():
    assert utils.playtime_to_str(60) == "1:00"
    assert utils.playtime_to_str(10) == "0:10"
    assert utils.playtime_to_str(0) == "0:00"
    assert utils.playtime_to_str(3600) == "60:00"
