import abc
import collections
import itertools

import attrs
import tabulate

from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.match_tracker import queries, utils
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
            str(self.first_player_score),
            "-",
            str(self.second_player_score),
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


class HeadToHead(Formatter):
    RECENT_MATCHES = 5
    UP_ARROW_EMOJI = "🔼"
    PAUSE_EMOJI = " ⏸️ "
    DOWN_ARROW_EMOJI = "🔽"

    @classmethod
    def format_matches(cls, matches: dataclasses.Matches, **kwargs) -> str:
        player_one = kwargs["player-one"]
        player_two = kwargs["player-two"]

        all_time_tally_data = queries.build_tally_data_by_player(matches)
        player_one_all_time = all_time_tally_data[player_one]
        player_two_all_time = all_time_tally_data[player_two]

        all_time_table_data = cls._all_time_table_data(player_one_all_time, player_two_all_time)
        table_data = all_time_table_data

        # If there are enough recent matches, display recent data
        recent_matches = matches.last(cls.RECENT_MATCHES)
        available_recent_matches = len(recent_matches)
        if available_recent_matches >= cls.RECENT_MATCHES:
            recent_tally_data = queries.build_tally_data_by_player(recent_matches)
            player_one_recent = recent_tally_data[player_one]
            player_two_recent = recent_tally_data[player_two]

            spacer = [["", "", ""]]
            recent_matches_header = [[f"Last {available_recent_matches} matches", "", ""]]
            recent_table_data = cls._recent_table_data(
                player_one_recent, player_two_recent, player_one_all_time, player_two_all_time
            )

            table_data += spacer + recent_matches_header + recent_table_data

        table_string = tabulate.tabulate(
            table_data,
            headers=(
                player_one.name,
                f"{player_one_all_time.number_matches}",
                player_two.name,
            ),
            stralign="center",
            numalign="center",
            maxcolwidths=[None, None, None],
            tablefmt="firstrow",
        )
        recent_match_strings = "\n".join(
            utils.build_match_string(match) for match in recent_matches.match_results
        )
        return f"```{table_string}```{recent_match_strings}"

    @classmethod
    def _all_time_table_data(
        cls,
        player_one_tally_data: queries.MatchesTallyData,
        player_two_tally_data: queries.MatchesTallyData,
    ) -> list[list[str]]:
        player_one_point_diff = (
            player_one_tally_data.total_score - player_two_tally_data.total_score
        )
        player_one_point_diff_str = (
            f"+{player_one_point_diff}"
            if player_one_point_diff > 0
            else f"{player_one_point_diff}"
        )
        player_two_point_diff = (
            player_two_tally_data.total_score - player_one_tally_data.total_score
        )
        player_two_point_diff_str = (
            f"+{player_two_point_diff}"
            if player_two_point_diff > 0
            else f"{player_two_point_diff}"
        )

        player_one_last_win_days_ago_str = cls._days_ago(player_one_tally_data.last_win_days_ago)
        player_two_last_win_days_ago_str = cls._days_ago(player_two_tally_data.last_win_days_ago)

        return [
            [
                f"{player_one_tally_data.wins}",
                "Wins",
                f"{player_two_tally_data.wins}",
            ],
            [
                f"{player_one_tally_data.win_rate}%",
                "Win rate",
                f"{player_two_tally_data.win_rate}%",
            ],
            [
                f"{player_one_tally_data.win_rate_serving}%",
                "Win rate (serving)",
                f"{player_two_tally_data.win_rate_serving}%",
            ],
            [
                player_one_point_diff_str,
                "Point diff.",
                player_two_point_diff_str,
            ],
            [
                f"{player_one_tally_data.average_score}",
                "Avg. score",
                f"{player_two_tally_data.average_score}",
            ],
            [
                f"{player_one_tally_data.current_win_streak}",
                "Current win streak",
                f"{player_two_tally_data.current_win_streak}",
            ],
            [
                f"{player_one_tally_data.highest_win_streak}",
                "Highest win streak",
                f"{player_two_tally_data.highest_win_streak}",
            ],
            [
                player_one_last_win_days_ago_str,
                "Last win",
                player_two_last_win_days_ago_str,
            ],
        ]

    @classmethod
    def _recent_table_data(
        cls,
        player_one_recent: queries.MatchesTallyData,
        player_two_recent: queries.MatchesTallyData,
        player_one_all_time: queries.MatchesTallyData,
        player_two_all_time: queries.MatchesTallyData,
    ) -> list[list[str]]:
        player_one_recent_win_rate_str = f"{cls._emoji(player_one_recent.win_rate, player_one_all_time.win_rate)} {player_one_recent.win_rate}%"
        player_two_recent_win_rate_str = f"{player_two_recent.win_rate}% {cls._emoji(player_two_recent.win_rate, player_two_all_time.win_rate)}"

        player_one_recent_win_rate_serving_str = f"{cls._emoji(player_one_recent.win_rate_serving, player_one_all_time.win_rate_serving)} {player_one_recent.win_rate_serving}%"
        player_two_recent_win_rate_serving_str = f"{player_two_recent.win_rate_serving}% {cls._emoji(player_two_recent.win_rate_serving, player_two_all_time.win_rate_serving)}"

        player_one_recent_avg_score_str = f"{cls._emoji(player_one_recent.average_score, player_one_all_time.average_score)} {player_one_recent.average_score}"
        player_two_recent_avg_score_str = f"{player_two_recent.average_score} {cls._emoji(player_two_recent.average_score, player_two_all_time.average_score)}"

        return [
            [
                player_one_recent_win_rate_str,
                "Win rate",
                player_two_recent_win_rate_str,
            ],
            [
                player_one_recent_win_rate_serving_str,
                "Win rate (serving)",
                player_two_recent_win_rate_serving_str,
            ],
            [
                player_one_recent_avg_score_str,
                "Avg. score",
                player_two_recent_avg_score_str,
            ],
        ]

    @classmethod
    def _emoji(cls, value_one: int, value_two: int) -> str:
        if value_one > value_two:
            return cls.UP_ARROW_EMOJI
        elif value_one == value_two:
            return cls.PAUSE_EMOJI
        else:
            return cls.DOWN_ARROW_EMOJI

    @classmethod
    def _days_ago(cls, days: int | None) -> str:
        if days is None:
            return "Never"
        elif days == 0:
            return "Today"
        elif days == 1:
            return "Yesterday"
        return f"{days} days ago"


def _match_string(match: dataclasses.MatchResult) -> str:
    return f"{match.served.name}\t{match.server_score} - {match.receiver_score}\t{match.receiver.name}"
