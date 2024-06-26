import datetime
import typing
import uuid

import attrs

from squash_bot.core.data import dataclasses as core_dataclasses


class FieldDoesNotExist(Exception):
    """
    Error raised when trying to sort by a field that does not exist
    """


class MatchNotFound(Exception):
    """
    Error raised when a match is not found
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

    @property
    def server_score(self) -> int:
        return self.winner_score if self.served == self.winner else self.loser_score

    @property
    def receiver(self) -> core_dataclasses.User:
        return self.loser if self.served == self.winner else self.winner

    @property
    def receiver_score(self) -> int:
        return self.winner_score if self.receiver == self.winner else self.loser_score

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

    def __len__(self) -> int:
        return len(self.match_results)

    def __add__(self, other: typing.Any) -> "Matches":
        if not isinstance(other, Matches):
            raise NotImplementedError
        return Matches(match_results=self.match_results + other.match_results)

    @classmethod
    def from_match_results(cls, match_results: list[dict[str, typing.Any]]) -> "Matches":
        return Matches(
            match_results=[MatchResult.from_dict(match_result) for match_result in match_results]
        )

    # Mutations
    # ---------

    def add(self, match_result: MatchResult) -> "Matches":
        return Matches(match_results=self.match_results + [match_result])

    def replace(self, match_result_to_replace: MatchResult) -> "Matches":
        """
        Replace a match result in the list of match results.

        The match result to replace is identified by its result_id.
        """
        return Matches(
            match_results=[
                match_result_to_replace
                if match_result_to_replace.result_id == match.result_id
                else match
                for match in self.match_results
            ]
        )

    # Queries
    # -------

    def sort_by(self, field: str, reverse: bool = False) -> "Matches":
        try:
            return Matches(
                match_results=sorted(
                    self.match_results, key=lambda x: getattr(x, field), reverse=reverse
                )
            )
        except AttributeError as e:
            raise FieldDoesNotExist(field) from e

    def from_date(self, from_date: datetime.date) -> "Matches":
        return Matches(
            match_results=[
                match_result
                for match_result in self.match_results
                if match_result.played_on >= from_date
            ]
        )

    def on_date(self, on_date: datetime.date) -> "Matches":
        return Matches(
            match_results=[
                match_result
                for match_result in self.match_results
                if match_result.played_on == on_date
            ]
        )

    def involves(self, user: core_dataclasses.User) -> "Matches":
        return Matches(
            match_results=[
                match_result
                for match_result in self.match_results
                if user in (match_result.winner, match_result.loser)
            ]
        )

    def last(self, n: int = 1) -> "Matches":
        return Matches(match_results=self.match_results[-n:])

    def match_by_id(self, result_id_str: str) -> MatchResult:
        result_id = uuid.UUID(result_id_str)
        for match_result in self.match_results:
            if match_result.result_id == result_id:
                return match_result
        raise MatchNotFound
