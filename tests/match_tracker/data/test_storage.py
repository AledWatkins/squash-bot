import datetime
import json

from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.match_tracker.data import dataclasses, storage
from squash_bot.settings import base as settings_base
from squash_bot.storage import base as storage_base

from tests.factories import core as core_factories
from tests.factories import match_tracker as match_tracker_factories


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
            served=core_dataclasses.User(id="1", username="winner", global_name="global-winner"),
            played_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_by=core_dataclasses.User(
                id="3", username="different-name", global_name="different-global-name"
            ),
        )
        fake_results = [result.to_dict()]
        guild = core_dataclasses.Guild(guild_id="1")
        storage_base.LocalStorage().store_file(
            file_path=settings_base.settings.MATCH_RESULTS_PATH,
            file_name=storage._results_file_name(guild),
            contents=json.dumps(fake_results),
        )

        assert storage.get_all_match_results_as_list(guild=guild) == [result.to_dict()]


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
            served=core_dataclasses.User(id="1", username="winner", global_name="global-winner"),
            played_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_by=core_dataclasses.User(
                id="3", username="different-name", global_name="different-global-name"
            ),
        )
        fake_results = [result.to_dict()]
        guild = core_dataclasses.Guild(guild_id="1")
        storage_base.LocalStorage().store_file(
            file_path=settings_base.settings.MATCH_RESULTS_PATH,
            file_name=storage._results_file_name(guild),
            contents=json.dumps(fake_results),
        )

        assert storage.get_all_match_results(guild).match_results == [result]


class TestReplaceMatchResult:
    def test_can_replace_result(self):
        ricky = core_factories.UserFactory(username="ricky")
        steve = core_factories.UserFactory(username="steve")
        karl = core_factories.UserFactory(username="karl")

        # Build three matches
        match_one = match_tracker_factories.MatchResultFactory(winner=ricky, loser=steve)
        match_two = match_tracker_factories.MatchResultFactory(winner=steve, loser=ricky)
        match_three = match_tracker_factories.MatchResultFactory(winner=karl, loser=steve)

        # Store those matches
        fake_results = [match_one.to_dict(), match_two.to_dict(), match_three.to_dict()]
        guild = core_dataclasses.Guild(guild_id="1")
        storage_base.LocalStorage().store_file(
            file_path=settings_base.settings.MATCH_RESULTS_PATH,
            file_name=storage._results_file_name(guild),
            contents=json.dumps(fake_results),
        )

        # Build a replacement match to replace the third match
        new_match_three = match_tracker_factories.MatchResultFactory(
            winner=steve, loser=karl, result_id=match_three.result_id
        )

        # Replace the third match with the new match
        storage.replace_match_result(match_result=new_match_three, guild=guild)

        # Check that the third match has been replaced
        assert storage.get_all_match_results(guild) == dataclasses.Matches(
            [match_one, match_two, new_match_three]
        )
