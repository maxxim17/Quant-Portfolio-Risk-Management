from pathlib import Path

from src.data.downloader import _safe_filename


def test_safe_filename():

    assert (
        _safe_filename("BRK.B")
        == "BRK_B"
    )


def test_safe_filename_uppercase():

    assert (
        _safe_filename("aapl")
        == "AAPL"
    )


def test_safe_filename_slash():

    assert (
        _safe_filename("ABC/DEF")
        == "ABC_DEF"
    )