import datetime
import uuid

from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.match_tracker.data import dataclasses

from tests.factories import core as core_factories
from tests.factories import match_tracker as match_tracker_factories


class TestMatchResult:
    def test_played_on(self):
        match_result = dataclasses.MatchResult(
            winner=core_dataclasses.User(id="1", username="winner", global_name="global-winner"),
            winner_score=11,
            loser_score=3,
            loser=core_dataclasses.User(id="2", username="loser", global_name="global-loser"),
            served=core_dataclasses.User(id="1", username="winner", global_name="global-winner"),
            played_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_by=core_dataclasses.User(
                id="1", username="different-user", global_name="global-different-user"
            ),
        )
        assert match_result.played_on == datetime.date(2021, 1, 1)

    def test_string_representation(self):
        match_result = dataclasses.MatchResult(
            winner=core_dataclasses.User(id="1", username="winner", global_name="global-winner"),
            winner_score=11,
            loser_score=3,
            loser=core_dataclasses.User(id="2", username="loser", global_name="global-loser"),
            served=core_dataclasses.User(id="1", username="winner", global_name="global-winner"),
            played_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_by=core_dataclasses.User(
                id="1", username="different-user", global_name="global-different-user"
            ),
        )
        assert str(match_result) == "winner beat loser 11-3 on 2021-01-01"

    def test_from_dict(self):
        match_result = dataclasses.MatchResult.from_dict(
            {
                "winner": {
                    "id": "1",
                    "username": "winner",
                    "global_name": "global-winner",
                },
                "winner_score": 11,
                "loser_score": 3,
                "loser": {
                    "id": "2",
                    "username": "loser",
                    "global_name": "global-loser",
                },
                "served": {
                    "id": "1",
                    "username": "winner",
                    "global_name": "global-winner",
                },
                "played_at": "2021-01-01T12:00:00",
                "logged_at": "2021-01-01T12:00:00",
                "logged_by": {
                    "id": "1",
                    "username": "different-user",
                    "global_name": "global-different-user",
                },
                "result_id": "00000000-0000-0000-0000-000000000000",
            }
        )
        assert match_result == dataclasses.MatchResult(
            winner=core_dataclasses.User(id="1", username="winner", global_name="global-winner"),
            winner_score=11,
            loser_score=3,
            loser=core_dataclasses.User(id="2", username="loser", global_name="global-loser"),
            served=core_dataclasses.User(id="1", username="winner", global_name="global-winner"),
            played_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_by=core_dataclasses.User(
                id="1", username="different-user", global_name="global-different-user"
            ),
            result_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
        )

    def test_receiver(self):
        match_result = match_tracker_factories.MatchResultFactory(loser_served=True)
        assert match_result.receiver == match_result.winner

    def test_receiver_score(self):
        match_result = match_tracker_factories.MatchResultFactory(loser_served=True)
        assert match_result.receiver_score == match_result.winner_score

    def test_server_score(self):
        match_result = match_tracker_factories.MatchResultFactory(loser_served=True)
        assert match_result.server_score == match_result.loser_score


class TestMatches:
    def test_sort_by_datetime(self):
        match_one = match_tracker_factories.MatchResultFactory(
            played_at=datetime.datetime(2021, 1, 1, 13, 0)
        )
        match_two = match_tracker_factories.MatchResultFactory(
            played_at=datetime.datetime(2021, 1, 1, 12, 0)
        )
        matches = dataclasses.Matches([match_one, match_two])

        sorted_matches = matches.sort_by("played_at")

        assert sorted_matches == dataclasses.Matches([match_two, match_one])

    def test_involves(self):
        player_one = core_factories.UserFactory()
        player_two = core_factories.UserFactory()
        player_three = core_factories.UserFactory()

        match_one = match_tracker_factories.MatchResultFactory(winner=player_one, loser=player_two)
        match_two = match_tracker_factories.MatchResultFactory(winner=player_two, loser=player_one)
        match_three = match_tracker_factories.MatchResultFactory(
            winner=player_three, loser=player_two
        )
        matches = dataclasses.Matches([match_one, match_two, match_three])

        involves_player_one = matches.involves(player_one)
        assert len(involves_player_one) == 2

        involves_player_two = matches.involves(player_two)
        assert len(involves_player_two) == 3

        involves_player_three = matches.involves(player_three)
        assert len(involves_player_three) == 1
