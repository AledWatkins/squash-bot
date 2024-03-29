import datetime
import json

from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.match_tracker.data import dataclasses, storage
from squash_bot.settings import base as settings_base
from squash_bot.storage import base as storage_base


class TestGetAllMatchResultsAsDict:
    def test_gets_results(self):
        result = dataclasses.MatchResult(
            winner=core_dataclasses.User(
                id="1", username="player_1", global_name="global-player_1"
            ),
            winner_score=11,
            loser_score=3,
            loser=core_dataclasses.User(
                id="2", username="player_2", global_name="global-player_2"
            ),
            played_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_by=core_dataclasses.User(
                id="3", username="different-name", global_name="different-global-name"
            ),
        )
        fake_results = [result.to_dict()]
        storage_base.LocalStorage().store_file(
            file_path=settings_base.settings.MATCH_RESULTS_PATH,
            file_name=settings_base.settings.MATCH_RESULTS_FILE,
            contents=json.dumps(fake_results),
        )

        assert storage.get_all_match_results_as_dict() == [result.to_dict()]


class TestGetAllMatchResults:
    def test_gets_results(self):
        result = dataclasses.MatchResult(
            winner=core_dataclasses.User(
                id="1", username="player_1", global_name="global-player_1"
            ),
            winner_score=11,
            loser_score=3,
            loser=core_dataclasses.User(
                id="2", username="player_2", global_name="global-player_2"
            ),
            played_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_by=core_dataclasses.User(
                id="3", username="different-name", global_name="different-global-name"
            ),
        )
        fake_results = [result.to_dict()]
        storage_base.LocalStorage().store_file(
            file_path=settings_base.settings.MATCH_RESULTS_PATH,
            file_name=settings_base.settings.MATCH_RESULTS_FILE,
            contents=json.dumps(fake_results),
        )

        assert storage.get_all_match_results() == [result]
