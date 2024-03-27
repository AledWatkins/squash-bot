import datetime

import attrs

from squash_bot.core.data import user


@attrs.frozen
class MatchResult:
    winner: user.User
    winner_score: int
    loser_score: int
    loser: user.User
    played_at: datetime.datetime
    logged_at: datetime.datetime

    @property
    def played_on(self) -> datetime.date:
        return self.played_at.date()

    def __str__(self):
        return f"{self.winner.username} beat {self.loser.username} {self.winner_score}-{self.loser_score} on {self.played_on.isoformat()}"
