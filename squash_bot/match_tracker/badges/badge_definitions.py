from collections import defaultdict
from decimal import Decimal

import attrs

from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.match_tracker.data import dataclasses as dataclasses

from . import badge


@attrs.frozen
class Crush(badge.Badge):
    """
    A crush is a game where the winner won without the loser scoring any points.
    """

    player: core_dataclasses.User
    opponent: core_dataclasses.User

    @property
    def display(self):
        return f"{self.player.name} crushed {self.opponent.name} 11-0"


class CrushCollector(badge.BadgeCollector[Crush]):
    def __init__(self) -> None:
        self._crushed_matches: set[dataclasses.MatchResult] = set()

    def mutate_context_for_match(self, match: dataclasses.MatchResult) -> None:
        if match.loser_score == 0:
            self._crushed_matches.add(match)

    def collect(self) -> list[Crush]:
        return [
            Crush(player=match.winner, opponent=match.loser, badge_earned_in=match)
            for match in self._crushed_matches
        ]


@attrs.frozen
class CleanSweep(badge.Badge):
    """
    A clean sweep is where the player won all of their games.
    """

    player: core_dataclasses.User

    @property
    def display(self):
        return f"{self.player.name} won all of their games"


class CleanSweepCollector(badge.BadgeCollector[CleanSweep]):
    def __init__(self) -> None:
        # Track the last win so we can associate it to the badge
        self._players_last_win: dict[core_dataclasses.User, dataclasses.MatchResult] = {}
        self._players: set[core_dataclasses.User] = set()
        self._players_with_loss: set[core_dataclasses.User] = set()

    def mutate_context_for_match(self, match: dataclasses.MatchResult) -> None:
        self._players.add(match.winner)
        self._players_last_win[match.winner] = match
        self._players_with_loss.add(match.loser)

    def collect(self) -> list[CleanSweep]:
        return [
            CleanSweep(player=player, badge_earned_in=self._players_last_win[player])
            for player in self._players - self._players_with_loss
        ]


@attrs.frozen
class WoodenSpoon(badge.Badge):
    """
    A wooden spoon is where the player lost all of their games.
    """

    player: core_dataclasses.User

    @property
    def display(self):
        return f"{self.player.name} lost all of their games"


class WoodenSpoonCollector(badge.BadgeCollector[WoodenSpoon]):
    def __init__(self) -> None:
        # Track the last loss so we can associate it to the badge
        self._players_last_loss: dict[core_dataclasses.User, dataclasses.MatchResult] = {}
        self._players: set[core_dataclasses.User] = set()
        self._players_with_win: set[core_dataclasses.User] = set()

    def mutate_context_for_match(self, match: dataclasses.MatchResult) -> None:
        self._players.add(match.loser)
        self._players_last_loss[match.loser] = match
        self._players_with_win.add(match.winner)

    def collect(self) -> list[WoodenSpoon]:
        return [
            WoodenSpoon(player=player, badge_earned_in=self._players_last_loss[player])
            for player in self._players - self._players_with_win
        ]


@attrs.frozen
class WinStreak(badge.Badge):
    """
    A win streak is where the player has won a certain number of games in a row.
    """

    player: core_dataclasses.User
    streak_length: int

    @property
    def display(self):
        return f"{self.player.name} had a {self.streak_length} game win streak"


class WinStreakCollector(badge.BadgeCollector[WinStreak]):
    min_streak_length = 3

    def __init__(self) -> None:
        self._streaks: list[WinStreak] = []
        self._players_last_win: dict[core_dataclasses.User, dataclasses.MatchResult] = {}
        self._current_streaks: dict[core_dataclasses.User, int] = defaultdict(int)

    def mutate_context_for_match(self, match: dataclasses.MatchResult) -> None:
        ended_streak = self._current_streaks[match.loser]
        if ended_streak >= self.min_streak_length:
            self._streaks.append(
                WinStreak(
                    player=match.loser,
                    streak_length=ended_streak,
                    badge_earned_in=self._players_last_win[match.loser],
                )
            )

        self._current_streaks[match.loser] = 0
        self._current_streaks[match.winner] += 1
        self._players_last_win[match.winner] = match

    def collect(self) -> list[WinStreak]:
        # Collect any ongoing streaks
        for player, streak_length in self._current_streaks.items():
            if streak_length >= self.min_streak_length:
                self._streaks.append(
                    WinStreak(
                        player=player,
                        streak_length=streak_length,
                        badge_earned_in=self._players_last_win[player],
                    )
                )

        return self._streaks


@attrs.frozen
class LossStreak(badge.Badge):
    """
    A loss streak is where the player has lost a certain number of games in a row.
    """

    player: core_dataclasses.User
    streak_length: int

    @property
    def display(self):
        return f"{self.player.name} had a {self.streak_length} game loss streak"


class LossStreakCollector(badge.BadgeCollector[LossStreak]):
    min_streak_length = 3

    def __init__(self) -> None:
        self._streaks: list[LossStreak] = []
        self._players_last_loss: dict[core_dataclasses.User, dataclasses.MatchResult] = {}
        self._current_streaks: dict[core_dataclasses.User, int] = defaultdict(int)

    def mutate_context_for_match(self, match: dataclasses.MatchResult) -> None:
        ended_streak = self._current_streaks[match.winner]
        if ended_streak >= self.min_streak_length:
            self._streaks.append(
                LossStreak(
                    player=match.winner,
                    streak_length=ended_streak,
                    badge_earned_in=self._players_last_loss[match.winner],
                )
            )

        self._current_streaks[match.winner] = 0
        self._current_streaks[match.loser] += 1
        self._players_last_loss[match.loser] = match

    def collect(self) -> list[LossStreak]:
        # Collect any ongoing streaks
        for player, streak_length in self._current_streaks.items():
            if streak_length >= self.min_streak_length:
                self._streaks.append(
                    LossStreak(
                        player=player,
                        streak_length=streak_length,
                        badge_earned_in=self._players_last_loss[player],
                    )
                )

        return self._streaks


@attrs.frozen
class StreakBreaker(badge.Badge):
    """
    A streak breaker is where the player has broken another player's win streak.
    """

    player: core_dataclasses.User
    opponent: core_dataclasses.User
    streak_length: int

    @property
    def display(self):
        return (
            f"{self.player.name} broke {self.opponent.name}'s {self.streak_length} game win streak"
        )


class StreakBreakerCollector(badge.BadgeCollector[StreakBreaker]):
    min_streak_length = 3

    def __init__(self) -> None:
        self._streaks: list[StreakBreaker] = []
        self._players_last_win: dict[core_dataclasses.User, dataclasses.MatchResult] = {}
        self._current_streaks: dict[core_dataclasses.User, int] = defaultdict(int)

    def mutate_context_for_match(self, match: dataclasses.MatchResult) -> None:
        ended_streak = self._current_streaks[match.loser]
        if ended_streak >= self.min_streak_length:
            self._streaks.append(
                StreakBreaker(
                    player=match.winner,
                    opponent=match.loser,
                    streak_length=ended_streak,
                    badge_earned_in=match,
                )
            )

        self._current_streaks[match.loser] = 0
        self._current_streaks[match.winner] += 1
        self._players_last_win[match.winner] = match

    def collect(self) -> list[StreakBreaker]:
        return self._streaks


@attrs.frozen
class FirstWinAgainst(badge.Badge):
    """
    A first win against is where the player has won their first game against another player.
    """

    player: core_dataclasses.User
    opponent: core_dataclasses.User

    @property
    def display(self):
        return f"{self.player.name} won their first game against {self.opponent.name}"


class FirstWinAgainstCollector(badge.BadgeCollector[FirstWinAgainst]):
    def __init__(self) -> None:
        self._first_wins: dict[
            tuple[core_dataclasses.User, core_dataclasses.User], dataclasses.MatchResult
        ] = {}

    def mutate_context_for_match(self, match: dataclasses.MatchResult) -> None:
        winner_loser = (match.winner, match.loser)
        if winner_loser not in self._first_wins:
            self._first_wins[winner_loser] = match

    def collect(self) -> list[FirstWinAgainst]:
        return [
            FirstWinAgainst(
                player=winner_loser[0],
                opponent=winner_loser[1],
                badge_earned_in=match,
            )
            for winner_loser, match in self._first_wins.items()
        ]


@attrs.frozen
class MVP(badge.Badge):
    """
    The MVP is the player who has the highest average point difference in a series of matches.
    """

    player: core_dataclasses.User
    average_point_difference: Decimal

    @property
    def display(self):
        return f"{self.player.name} had the highest average point difference of {self.average_point_difference:+}"


class MVPCollector(badge.BadgeCollector[MVP]):
    def __init__(self) -> None:
        self._point_differences: dict[core_dataclasses.User, int] = defaultdict(int)
        self._num_matches: dict[core_dataclasses.User, int] = defaultdict(int)
        # We associate the badge with the last match played by the player
        self._player_last_match: dict[core_dataclasses.User, dataclasses.MatchResult] = {}

    def mutate_context_for_match(self, match: dataclasses.MatchResult) -> None:
        point_difference = match.winner_score - match.loser_score
        self._num_matches[match.winner] += 1
        self._num_matches[match.loser] += 1

        self._point_differences[match.winner] += point_difference
        self._player_last_match[match.winner] = match

        self._point_differences[match.loser] -= point_difference
        self._player_last_match[match.loser] = match

    def collect(self) -> list[MVP]:
        highest_point_diff = Decimal(0)
        player_with_highest = None
        for player in self._point_differences:
            avg_point_diff = Decimal(
                self._point_differences[player] / self._num_matches[player]
            ).quantize(Decimal("0.01"))
            if avg_point_diff > highest_point_diff:
                highest_point_diff = avg_point_diff
                player_with_highest = player

        if not player_with_highest:
            return []

        return [
            MVP(
                player=player_with_highest,
                average_point_difference=highest_point_diff,
                badge_earned_in=self._player_last_match[player_with_highest],
            )
        ]


badge_collector_mapping: dict[type[badge.Badge], type[badge.BadgeCollector]] = {
    Crush: CrushCollector,
    CleanSweep: CleanSweepCollector,
    WoodenSpoon: WoodenSpoonCollector,
    WinStreak: WinStreakCollector,
    LossStreak: LossStreakCollector,
    StreakBreaker: StreakBreakerCollector,
    FirstWinAgainst: FirstWinAgainstCollector,
    MVP: MVPCollector,
}
