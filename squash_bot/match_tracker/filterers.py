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


class LastN(Filterer):
    @classmethod
    def filter(cls, matches: dataclasses.Matches, **kwargs) -> dataclasses.Matches:
        n = 15
        return matches.last(n)


class OptionalFromDateFilterer(Filterer):
    @classmethod
    def filter(cls, matches: dataclasses.Matches, **kwargs) -> dataclasses.Matches:
        if from_date_string := kwargs.get("include-matches-from"):
            from_date = datetime.date.fromisoformat(from_date_string)
            matches = matches.from_date(from_date)
        return matches


class LastSessionOrDate(Filterer):
    """
    Filter matches for a specific date or all the matches from the last day of play.
    """

    @classmethod
    def filter(cls, matches: dataclasses.Matches, **kwargs) -> dataclasses.Matches:
        if date_string := kwargs.get("date"):
            date = datetime.date.fromisoformat(date_string)
        else:
            # This is going to be a problem if there are no matches, but I don't care right now
            date = matches.match_results[-1].played_on

        return matches.on_date(date)


class HeadToHead(Filterer):
    @classmethod
    def filter(cls, matches: dataclasses.Matches, **kwargs) -> dataclasses.Matches:
        return matches.involves(kwargs["player-one"]).involves(kwargs["player-two"])
