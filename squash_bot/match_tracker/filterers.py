import abc

from squash_bot.match_tracker.data import dataclasses


class Filterer(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def filter(cls, matches: dataclasses.Matches, **kwargs) -> dataclasses.Matches: ...


class NoopFilterer(Filterer):
    @classmethod
    def filter(cls, matches: dataclasses.Matches, **kwargs) -> dataclasses.Matches:
        return matches
