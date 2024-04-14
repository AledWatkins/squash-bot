import typing

import attrs

from squash_bot.match_tracker.data import dataclasses as dataclasses


@attrs.frozen
class Badge:
    """
    A class to represent a type of "badge" for a match or series of matches.
    """

    badge_earned_in: dataclasses.MatchResult = attrs.field(eq=False, hash=False)

    @property
    def display(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.display} ({self.badge_earned_in.played_on.isoformat()})"


T_badge = typing.TypeVar("T_badge", bound=Badge)


class BadgeCollector(typing.Generic[T_badge]):
    """
    A class which implements the logic to collect a specific badge for a series of matches.
    """

    def mutate_context_for_match(self, match: dataclasses.MatchResult) -> None:
        """
        This method should be implemented by the subclass to update any class context for the current match.
        """

    def collect(self) -> list[T_badge]:
        """
        This method should be implemented by the subclass to build / return any badges that have been earned.
        """
        return []
