import datetime

from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.match_tracker.data import dataclasses


class TestMatchResult:
    def test_played_on(self):
        match_result = dataclasses.MatchResult(
            winner=core_dataclasses.User(id="1", username="winner", global_name="global-winner"),
            winner_score=11,
            loser_score=3,
            loser=core_dataclasses.User(id="2", username="loser", global_name="global-loser"),
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
                "played_at": "2021-01-01T12:00:00",
                "logged_at": "2021-01-01T12:00:00",
                "logged_by": {
                    "id": "1",
                    "username": "different-user",
                    "global_name": "global-different-user",
                },
            }
        )
        assert match_result == dataclasses.MatchResult(
            winner=core_dataclasses.User(id="1", username="winner", global_name="global-winner"),
            winner_score=11,
            loser_score=3,
            loser=core_dataclasses.User(id="2", username="loser", global_name="global-loser"),
            played_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_by=core_dataclasses.User(
                id="1", username="different-user", global_name="global-different-user"
            ),
        )
