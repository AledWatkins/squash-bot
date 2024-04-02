import abc

from squash_bot.match_tracker.data import dataclasses


class Filterer(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def filter(self, matches: dataclasses.Matches) -> dataclasses.Matches: ...
