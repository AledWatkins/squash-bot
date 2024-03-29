import datetime
import typing
import uuid

import attrs

from squash_bot.core.data import dataclasses as core_dataclasses


class FieldDoesNotExist(Exception):
    """
    Error raised when trying to sort by a field that does not exist
    """


@attrs.frozen
class MatchResult:
    winner: core_dataclasses.User
    winner_score: int
    loser_score: int
    loser: core_dataclasses.User
    served: core_dataclasses.User
    played_at: datetime.datetime
    logged_at: datetime.datetime
    logged_by: core_dataclasses.User
    result_id: uuid.UUID = attrs.Factory(uuid.uuid4)

    @property
    def played_on(self) -> datetime.date:
        return self.played_at.date()

    def __str__(self):
        return f"{self.winner.username} beat {self.loser.username} {self.winner_score}-{self.loser_score} on {self.played_on.isoformat()}"

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]) -> "MatchResult":
        return MatchResult(
            winner=core_dataclasses.User.from_dict(data["winner"]),
            winner_score=data["winner_score"],
            loser_score=data["loser_score"],
            loser=core_dataclasses.User.from_dict(data["loser"]),
            served=core_dataclasses.User.from_dict(data["served"]),
            played_at=datetime.datetime.fromisoformat(data["played_at"]),
            logged_at=datetime.datetime.fromisoformat(data["logged_at"]),
            logged_by=core_dataclasses.User.from_dict(data["logged_by"]),
            result_id=uuid.UUID(data["result_id"]),
        )

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            "winner": core_dataclasses.User.to_dict(self.winner),
            "winner_score": self.winner_score,
            "loser_score": self.loser_score,
            "loser": core_dataclasses.User.to_dict(self.loser),
            "served": core_dataclasses.User.to_dict(self.served),
            "played_at": self.played_at.isoformat(),
            "logged_at": self.logged_at.isoformat(),
            "logged_by": core_dataclasses.User.to_dict(self.logged_by),
            "result_id": str(self.result_id),
        }


@attrs.frozen
class Matches:
    match_results: list[MatchResult]

    def __bool__(self) -> bool:
        return bool(self.match_results)

    @classmethod
    def from_match_results(cls, match_results: list[dict[str, typing.Any]]) -> "Matches":
        return Matches(
            match_results=[MatchResult.from_dict(match_result) for match_result in match_results]
        )

    def add(self, match_result: MatchResult) -> "Matches":
        return Matches(match_results=self.match_results + [match_result])

    def sort_by(self, field: str, reverse: bool = False) -> "Matches":
        try:
            return Matches(
                match_results=sorted(
                    self.match_results, key=lambda x: getattr(x, field), reverse=reverse
                )
            )
        except AttributeError as e:
            raise FieldDoesNotExist(field) from e
