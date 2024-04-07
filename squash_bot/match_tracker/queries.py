import collections
import datetime

import attrs

from squash_bot.core.data import dataclasses as core_dataclasses
from squash_bot.match_tracker.data import dataclasses, storage


def get_matches(guild: core_dataclasses.Guild) -> dataclasses.Matches:
    return storage.get_all_match_results(guild=guild)


@attrs.define
class MatchesTallyData:
    number_matches: int = 0
    wins: int = 0
    total_score: int = 0
    matches_served: int = 0
    wins_served: int = 0
    matches_received: int = 0
    wins_received: int = 0
    highest_win_streak: int = 0
    highest_loss_streak: int = 0
    last_win_datetime: datetime.datetime | None = None

    current_win_streak: int = 0
    current_loss_streak: int = 0

    @property
    def losses(self) -> int:
        return self.number_matches - self.wins

    @property
    def losses_served(self) -> int:
        return self.matches_served - self.wins_served

    @property
    def losses_received(self) -> int:
        return self.matches_received - self.wins_received

    @property
    def win_rate(self) -> int:
        return int((self.wins / self.number_matches) * 100)

    @property
    def win_rate_serving(self) -> int | None:
        if not self.matches_served:
            return None
        return int((self.wins_served / self.matches_served) * 100)

    @property
    def average_score(self) -> int:
        return self.total_score // self.number_matches

    @property
    def last_win_days_ago(self) -> int | None:
        if self.last_win_datetime:
            return (datetime.datetime.now() - self.last_win_datetime).days
        return None

    def record_win(self, match: dataclasses.MatchResult) -> None:
        self.number_matches += 1
        self.total_score += match.winner_score
        self.wins += 1

        served = match.served == match.winner
        self.matches_served += int(served)
        self.wins_served += int(served)
        self.matches_received += int(not served)
        self.wins_received += int(not served)

        self.current_win_streak += 1
        self.current_loss_streak = 0
        self.highest_win_streak = max(self.highest_win_streak, self.current_win_streak)
        self.last_win_datetime = match.played_at

    def record_loss(self, match: dataclasses.MatchResult) -> None:
        self.number_matches += 1
        self.total_score += match.loser_score

        served = match.served == match.loser
        self.matches_served += int(served)
        self.matches_received += int(not served)

        self.current_loss_streak += 1
        self.current_win_streak = 0
        self.highest_loss_streak = max(self.highest_loss_streak, self.current_loss_streak)


def build_tally_data_by_player(
    matches: dataclasses.Matches,
) -> dict[core_dataclasses.User, MatchesTallyData]:
    player_tally: dict[core_dataclasses.User, MatchesTallyData] = collections.defaultdict(
        MatchesTallyData
    )
    for match in matches.match_results:
        player_tally[match.winner].record_win(match)
        player_tally[match.loser].record_loss(match)

    return player_tally
