import datetime

import pytest

from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.match_tracker import validate
from squash_bot.match_tracker.data import dataclasses


class TestValidateMatchResult:
    @pytest.mark.parametrize(
        "winner_score, loser_score, error_message",
        [
            (11, 12, "Winner score must be greater than loser score"),
            (13, 12, "Winner must win by 2 points if they score more than 11 points"),
            (11, 11, "Cannot have a draw"),
            (10, 1, "Winner must score at least 11 points"),
            (11, -1, "Scores must be positive"),
        ],
    )
    def test_validate_score(self, winner_score, loser_score, error_message):
        match_result = dataclasses.MatchResult(
            winner=core_dataclasses.User(id="1", username="winner", global_name="global-winner"),
            winner_score=winner_score,
            loser=core_dataclasses.User(id="2", username="loser", global_name="global-loser"),
            loser_score=loser_score,
            served=core_dataclasses.User(id="1", username="winner", global_name="global-winner"),
            played_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_by=core_dataclasses.User(
                id="3", username="different-name", global_name="different-global-name"
            ),
        )
        with pytest.raises(validate.ValidationError, match=error_message):
            validate.validate_match_result(match_result)

    def test_validate_same_player(self):
        match_result = dataclasses.MatchResult(
            winner=core_dataclasses.User(id="1", username="winner", global_name="global-winner"),
            winner_score=11,
            loser=core_dataclasses.User(id="1", username="winner", global_name="global-winner"),
            loser_score=3,
            served=core_dataclasses.User(id="1", username="winner", global_name="global-winner"),
            played_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_by=core_dataclasses.User(
                id="3", username="different-name", global_name="different-global-name"
            ),
        )
        with pytest.raises(
            validate.ValidationError, match="Winner and loser must be different players"
        ):
            validate.validate_match_result(match_result)

    def test_validate_server(self):
        match_result = dataclasses.MatchResult(
            winner=core_dataclasses.User(id="1", username="winner", global_name="global-winner"),
            winner_score=11,
            loser=core_dataclasses.User(id="2", username="loser", global_name="global-loser"),
            loser_score=3,
            served=core_dataclasses.User(
                id="3", username="different", global_name="global-different"
            ),
            played_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_at=datetime.datetime(2021, 1, 1, 12, 0),
            logged_by=core_dataclasses.User(
                id="3", username="different-name", global_name="different-global-name"
            ),
        )
        with pytest.raises(
            validate.ValidationError,
            match="The player who served must be one of the players in the match",
        ):
            validate.validate_match_result(match_result)
