import abc

from squash_bot.match_tracker.data import dataclasses


class Orderer(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def order(self, matches: dataclasses.Matches) -> dataclasses.Matches: ...
