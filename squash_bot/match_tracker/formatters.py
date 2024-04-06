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


@attrs.frozen
class MatchRow:
    first_player: core_dataclasses.User
    first_player_score: int
    second_player_score: int
    second_player: core_dataclasses.User

    def as_display_row(self) -> list[str]:
        return [
            "\t",
            self.first_player.name,
            self.first_player_score,
            "-",
            self.second_player_score,
            self.second_player.name,
        ]


class PlayedAtFormatter(Formatter):
    @classmethod
    def format_matches(cls, matches: dataclasses.Matches, **kwargs) -> str:
        groups = itertools.groupby(matches.match_results, key=lambda match: match.played_on)

        inner_message = ""
        for played_at, match_results in groups:
            pretty_date = played_at.strftime("%A, %-d %B %Y")
            inner_message += f"\n\n{pretty_date}:\n"
            inner_message += tabulate.tabulate(
                [
                    MatchRow(
                        first_player=match.served,
                        first_player_score=match.server_score,
                        second_player_score=match.receiver_score,
                        second_player=match.receiver,
                    ).as_display_row()
                    for match in match_results
                ],
                tablefmt="plain",
            )

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
    return f"{match.served.name}\t{match.server_score} - {match.receiver_score}\t{match.receiver.name}"
