import pathlib


def fixture_path(filepath: str) -> pathlib.Path:
    return pathlib.Path(__file__).parent / "fixtures" / filepath
