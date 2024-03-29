from squash_bot.match_tracker.data import dataclasses


class ValidationError(Exception):
    """
    Base class for validation errors
    """


def validate_match_result(match_result: dataclasses.MatchResult) -> None:
    if match_result.winner_score < 11:
        raise ValidationError("Winner must score at least 11 points")

    if match_result.winner_score < match_result.loser_score:
        raise ValidationError("Winner score must be greater than loser score")

    if match_result.winner_score == match_result.loser_score:
        raise ValidationError("Cannot have a draw")

    if match_result.winner_score < 0 or match_result.loser_score < 0:
        raise ValidationError("Scores must be positive")

    if (
        match_result.winner_score > 11
        and match_result.winner_score - match_result.loser_score != 2
    ):
        raise ValidationError("Winner must win by 2 points if they score more than 11 points")

    if match_result.winner == match_result.loser:
        raise ValidationError("Winner and loser must be different players")

    if match_result.served not in (match_result.winner, match_result.loser):
        raise ValidationError("The player who served must be one of the players in the match")
