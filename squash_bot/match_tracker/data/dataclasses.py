import attrs

from squash_bot.core.data import user


@attrs.frozen
class MatchResult:
    winner: user.User
    winner_score: int
    loser_score: int
    loser: user.User
