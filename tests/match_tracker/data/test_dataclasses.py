import datetime

from squash_bot.core.data import user
from squash_bot.match_tracker.data import dataclasses


class TestMatchResult:
    def test_played_on(self):
        match_result = dataclasses.MatchResult(
            winner=user.User(id="1", username="winner", global_name="global-winner"),
            winner_score=11,
            loser_score=3,
            loser=user.User(id="2", username="loser", global_name="global-loser"),
            played_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_at=datetime.datetime(2021, 1, 1, 12, 0),
        )
        assert match_result.played_on == datetime.date(2021, 1, 1)

    def test_string_representation(self):
        match_result = dataclasses.MatchResult(
            winner=user.User(id="1", username="winner", global_name="global-winner"),
            winner_score=11,
            loser_score=3,
            loser=user.User(id="2", username="loser", global_name="global-loser"),
            played_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_at=datetime.datetime(2021, 1, 1, 12, 0),
        )
        assert str(match_result) == "winner beat loser 11-3 on 2021-01-01"
