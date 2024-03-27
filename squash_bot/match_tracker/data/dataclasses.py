import datetime
import typing

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

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> "MatchResult":
        return MatchResult(
            winner=user.User.from_dict(data["winner"]),
            winner_score=data["winner_score"],
            loser_score=data["loser_score"],
            loser=user.User.from_dict(data["loser"]),
            played_at=datetime.datetime.fromisoformat(data["played_at"]),
            logged_at=datetime.datetime.fromisoformat(data["logged_at"]),
        )

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            "winner": user.User.to_dict(self.winner),
            "winner_score": self.winner_score,
            "loser_score": self.loser_score,
            "loser": user.User.to_dict(self.loser),
            "played_at": self.played_at.isoformat(),
            "logged_at": self.logged_at.isoformat(),
        }
