import abc
import datetime

from squash_bot.match_tracker.data import dataclasses


class Filterer(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def filter(cls, matches: dataclasses.Matches, **kwargs) -> dataclasses.Matches: ...


class NoopFilterer(Filterer):
    @classmethod
    def filter(cls, matches: dataclasses.Matches, **kwargs) -> dataclasses.Matches:
        return matches


class OptionalFromDateFilterer(Filterer):
    @classmethod
    def filter(cls, matches: dataclasses.Matches, **kwargs) -> dataclasses.Matches:
        if from_date_string := kwargs.get("include-matches-from"):
            from_date = datetime.date.fromisoformat(from_date_string)
            matches = matches.from_date(from_date)
        return matches


class HeadToHead(Filterer):
    @classmethod
    def filter(cls, matches: dataclasses.Matches, **kwargs) -> dataclasses.Matches:
        return matches.involves(kwargs["player-one"]).involves(kwargs["player-two"])
