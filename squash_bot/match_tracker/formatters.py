import abc
import itertools

from squash_bot.match_tracker.data import dataclasses


class Formatter(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def format_matches(cls, matches: dataclasses.Matches) -> str: ...


class PlayedAtFormatter(Formatter):
    @classmethod
    def format_matches(cls, matches: dataclasses.Matches) -> str:
        groups = itertools.groupby(
            sorted(matches.match_results, key=lambda match: match.played_at),
            key=lambda match: match.played_at,
        )

        inner_message = ""
        for played_at, matches in groups:
            pretty_date = played_at.strftime("%A, %-d %B %Y")
            inner_message += f"\n\n{pretty_date}:"
            for match in matches:
                inner_message += f"\n\t{match}"

        return f"```{inner_message}```"

    def _match_string(self, match: dataclasses.MatchResult) -> str:
        served_marker = "*"
        if match.served == match.winner:
            winner_name = f"{match.winner.name}{served_marker}"
            loser_name = f"{match.loser.name}"
        else:
            winner_name = f"{match.winner.name}"
            loser_name = f"{match.loser.name}{served_marker}"

        return f"{winner_name} {match.winner_score} - {match.loser_score} {loser_name}"
