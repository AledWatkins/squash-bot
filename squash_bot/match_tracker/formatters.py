import abc
import collections
import itertools
from decimal import Decimal

import attrs
import tabulate

from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.match_tracker import queries
from squash_bot.match_tracker.badges import priority
from squash_bot.match_tracker.badges import queries as badge_queries
from squash_bot.match_tracker.data import dataclasses

from . import filterers


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
    result_id: str | None = None

    def as_display_row(self) -> list[str]:
        additional_columns = []
        if self.result_id:
            additional_columns.append(f"({self.result_id})")
        return [
            "\t",
            self.first_player.name,
            str(self.first_player_score),
            "-",
            str(self.second_player_score),
            self.second_player.name,
        ] + additional_columns


class PlayedAtFormatter(Formatter):
    @classmethod
    def format_matches(cls, matches: dataclasses.Matches, **kwargs) -> str:
        with_ids = kwargs.get("with-ids", False)
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
                        result_id=str(match.result_id) if with_ids else None,
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
        return f"```{table_string}```"

    @classmethod
    def _all_time_table_data(
        cls,
        player_one_tally_data: queries.MatchesTallyData,
        player_two_tally_data: queries.MatchesTallyData,
    ) -> list[list[str]]:
        player_one_win_rate_serving_str = cls._nullable_percentage_string(
            player_one_tally_data.win_rate_serving
        )
        player_two_win_rate_serving_str = cls._nullable_percentage_string(
            player_two_tally_data.win_rate_serving
        )

        total_point_diff = player_one_tally_data.total_score - player_two_tally_data.total_score

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
                player_one_win_rate_serving_str,
                "Win rate (serving)",
                player_two_win_rate_serving_str,
            ],
            [
                f"{total_point_diff:+}",
                "Point diff.",
                f"{total_point_diff*-1:+}",
            ],
            [
                f"{player_one_tally_data.average_point_difference_str}",
                "Avg. point diff.",
                f"{player_two_tally_data.average_point_difference_str}",
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

        player_one_win_rate_serving_str = cls._nullable_percentage_string(
            player_one_recent.win_rate_serving
        )
        player_two_win_rate_serving_str = cls._nullable_percentage_string(
            player_two_recent.win_rate_serving
        )

        player_one_recent_win_rate_serving_str = f"{cls._emoji(player_one_recent.win_rate_serving, player_one_all_time.win_rate_serving)} {player_one_win_rate_serving_str}"
        player_two_recent_win_rate_serving_str = f"{player_two_win_rate_serving_str} {cls._emoji(player_two_recent.win_rate_serving, player_two_all_time.win_rate_serving)}"

        player_one_recent_avg_pt_diff_str = f"{cls._emoji(player_one_recent.average_point_difference, player_one_all_time.average_point_difference)} {player_one_recent.average_point_difference_str}"
        player_two_recent_avg_pt_diff_str = f"{player_two_recent.average_point_difference_str} {cls._emoji(player_two_recent.average_point_difference, player_two_all_time.average_point_difference)}"

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
                player_one_recent_avg_pt_diff_str,
                "Avg. point diff.",
                player_two_recent_avg_pt_diff_str,
            ],
        ]

    @classmethod
    def _emoji(cls, value_one: Decimal | int | None, value_two: Decimal | int | None) -> str:
        if value_one is None or value_two is None:
            return ""
        elif value_one > value_two:
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

    @classmethod
    def _nullable_percentage_string(cls, value: int | None) -> str:
        return f"{value}%" if value is not None else "-"


class SessionSummary(Formatter):
    @classmethod
    def format_matches(cls, matches: dataclasses.Matches, **kwargs) -> str:
        # We pass in all matches so we can build all-time badges but we only display the last session worth of matches
        session_matches = filterers.LastSessionOrDate().filter(matches, **kwargs)
        session_date = session_matches.match_results[0].played_on
        session_date_pretty = session_date.strftime("%A, %-d %B %Y")

        tally_data = queries.build_tally_data_by_player(session_matches)
        player_rows = []
        for player, data in tally_data.items():
            player_rows.append(
                LeagueTableRow(
                    player=player,
                    wins=data.wins,
                    losses=data.losses,
                    win_percentage=data.win_rate,
                )
            )

        sorted_player_rows = sorted(player_rows, key=lambda row: row.win_percentage, reverse=True)
        table_str = tabulate.tabulate(
            [row.as_display_row() for row in sorted_player_rows],
            LeagueTableRow.display_headers(),
            tablefmt="firstrow",
        )

        # Collect badges
        badges = []
        badges += badge_queries.collect_badges(matches, badge_queries.default_all_time_badges)
        badges += badge_queries.collect_badges(
            session_matches, badge_queries.default_session_badges
        )
        badges = badge_queries.filter_badges_by_session(
            badges, session_matches.match_results[-1].played_on
        )

        # Sort by priority and only show the top 5
        badges_in_priority_order = sorted(
            badges, key=lambda badge: priority.get_priority(badge), reverse=True
        )
        badges_to_show = badge_queries.deduplicate_badges(badges_in_priority_order)
        sorted_badges_to_show = sorted(
            badges_to_show, key=lambda badge: priority.get_priority(badge), reverse=True
        )[:5]
        badges_text = "\n".join(badge.display for badge in sorted_badges_to_show)

        return f"Session: {session_date_pretty}```{table_str}```\n{badges_text}"


def _match_string(match: dataclasses.MatchResult) -> str:
    return f"{match.served.name}\t{match.server_score} - {match.receiver_score}\t{match.receiver.name}"
