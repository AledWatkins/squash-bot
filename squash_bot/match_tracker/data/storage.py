import json

from squash_bot.match_tracker.data import dataclasses
from squash_bot.settings import base as settings_base
from squash_bot.storage import base


def get_all_match_results_as_dict() -> dict:
    file_contents = base.get_storage_backend().read_file(
        file_path=settings_base.settings.MATCH_RESULTS_PATH,
        file_name=settings_base.settings.MATCH_RESULTS_FILE,
    )
    return json.loads(file_contents)


def get_all_match_results() -> list[dataclasses.MatchResult]:
    return [
        dataclasses.MatchResult.from_dict(result) for result in get_all_match_results_as_dict()
    ]
