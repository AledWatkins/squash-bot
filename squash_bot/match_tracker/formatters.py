import abc
import collections
import itertools

from squash_bot.match_tracker.data import dataclasses


class Formatter(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def format_matches(cls, matches: dataclasses.Matches) -> str: ...


class PlayedAtFormatter(Formatter):
    @classmethod
    def format_matches(cls, matches: dataclasses.Matches) -> str:
        groups = itertools.groupby(matches.match_results, key=lambda match: match.played_on)

        inner_message = ""
        for played_at, matches in groups:
            pretty_date = played_at.strftime("%A, %-d %B %Y")
            inner_message += f"\n\n{pretty_date}:"
            for match in matches:
                match_string = _match_string(match)
                inner_message += f"\n\t{match_string}"

        return f"```{inner_message}```"


class LeagueTable(Formatter):
    @classmethod
    def format_matches(cls, matches: dataclasses.Matches) -> str:
        player_results = collections.defaultdict(dict)
        for match in matches.match_results:
            player_results[match.winner]["wins"] = player_results[match.winner].get("wins", 0) + 1
            player_results[match.loser]["losses"] = (
                player_results[match.loser].get("losses", 0) + 1
            )

            point_difference = match.winner_score - match.loser_score
            player_results[match.winner]["point_difference"] = (
                player_results[match.winner].get("point_difference", 0) + point_difference
            )
            player_results[match.loser]["point_difference"] = (
                player_results[match.loser].get("point_difference", 0) - point_difference
            )

        inner_message = ""
        for player, results in player_results.items():
            wins = results.get("wins", 0)
            losses = results.get("losses", 0)
            point_difference = results.get("point_difference", 0)
            inner_message += f"\n{player.name}\t{wins}\t{losses}\t{point_difference}"

        return f"```Player\tWins\tLosses\tPoint Difference\n{inner_message}```"


def _match_string(match: dataclasses.MatchResult) -> str:
    served_marker = "*"
    if match.served == match.winner:
        winner_name = f"{match.winner.name}{served_marker}"
        loser_name = f"{match.loser.name}"
    else:
        winner_name = f"{match.winner.name}"
        loser_name = f"{match.loser.name}{served_marker}"

    return f"{winner_name}\t{match.winner_score} - {match.loser_score}\t{loser_name}"
