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
