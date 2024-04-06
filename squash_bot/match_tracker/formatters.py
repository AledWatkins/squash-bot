import abc
import collections
import itertools

import attrs
import tabulate

from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.match_tracker.data import dataclasses


class Formatter(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def format_matches(cls, matches: dataclasses.Matches, **kwargs) -> str: ...


class BasicFormatter(Formatter):
    @classmethod
    def format_matches(cls, matches: dataclasses.Matches, **kwargs) -> str:
        inner_message = "\n".join(_match_string(match) for match in matches.match_results)
        return f"```{inner_message}```"


class PlayedAtFormatter(Formatter):
    @classmethod
    def format_matches(cls, matches: dataclasses.Matches, **kwargs) -> str:
        groups = itertools.groupby(matches.match_results, key=lambda match: match.played_on)

        inner_message = ""
        for played_at, match_results in groups:
            pretty_date = played_at.strftime("%A, %-d %B %Y")
            inner_message += f"\n\n{pretty_date}:"
            for match in match_results:
                match_string = _match_string(match)
                inner_message += f"\n\t{match_string}"

        return f"```{inner_message}```"


@attrs.frozen
class LeagueTableRow:
    player: core_dataclasses.User
    wins: int
    losses: int
    win_percentage: int

    def as_display_row(self) -> list[str]:
        return [self.player.name, str(self.wins), str(self.losses), f"{self.win_percentage}%"]

    @classmethod
    def display_headers(cls) -> list[str]:
        return ["Player", "Wins", "Losses", "Win %"]


class LeagueTable(Formatter):
    @classmethod
    def format_matches(cls, matches: dataclasses.Matches, **kwargs) -> str:
        player_results: dict[core_dataclasses.User, dict] = collections.defaultdict(dict)
        for match in matches.match_results:
            player_results[match.winner]["wins"] = player_results[match.winner].get("wins", 0) + 1
            player_results[match.loser]["losses"] = (
                player_results[match.loser].get("losses", 0) + 1
            )

        player_rows = []
        for player, results in player_results.items():
            wins = results.get("wins", 0)
            losses = results.get("losses", 0)
            total_games = wins + losses
            win_percentage = int((wins / total_games) * 100)

            player_rows.append(
                LeagueTableRow(
                    player=player, wins=wins, losses=losses, win_percentage=win_percentage
                )
            )

        # Sort by descending win percentage
        player_rows = sorted(player_rows, key=lambda row: row.win_percentage, reverse=True)

        player_rows_display = [row.as_display_row() for row in player_rows]
        inner_message = tabulate.tabulate(
            player_rows_display, LeagueTableRow.display_headers(), tablefmt="rounded_grid"
        )

        return f"```{inner_message}```"


def _match_string(match: dataclasses.MatchResult) -> str:
    served_marker = "*"
    if match.served == match.winner:
        winner_name = f"{match.winner.name}{served_marker}"
        loser_name = f"{match.loser.name}"
    else:
        winner_name = f"{match.winner.name}"
        loser_name = f"{match.loser.name}{served_marker}"

    return f"{winner_name}\t{match.winner_score} - {match.loser_score}\t{loser_name}"
