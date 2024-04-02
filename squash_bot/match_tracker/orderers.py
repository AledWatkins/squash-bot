import abc

from squash_bot.match_tracker.data import dataclasses


class Orderer(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def order(cls, matches: dataclasses.Matches, **kwargs) -> dataclasses.Matches: ...


class NoopOrderer(Orderer):
    @classmethod
    def order(cls, matches: dataclasses.Matches, **kwargs) -> dataclasses.Matches:
        return matches
