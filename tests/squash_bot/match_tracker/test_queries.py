import datetime

import time_machine

from squash_bot.match_tracker import queries
from squash_bot.match_tracker.data import dataclasses

from tests.factories import core as core_factories
from tests.factories import match_tracker as match_tracker_factories


class TestBuildTallyDataByPlayer:
    def test_returns_correct_win_loss_data(self):
        player_one = core_factories.UserFactory(username="player one")
        player_two = core_factories.UserFactory(username="player two")
        matches = match_tracker_factories.build_match_history_between(
            player_one, player_two, games_played=10
        )

        tally_data = queries.build_tally_data_by_player(matches)
        assert len(tally_data.keys()) == 2

        player_one_tally = tally_data[player_one]
        player_two_tally = tally_data[player_two]
        assert player_one_tally.number_matches == 10
        assert player_two_tally.number_matches == 10

        assert player_one_tally.wins == player_two_tally.losses
        assert player_one_tally.losses == player_two_tally.wins

        assert (
            player_one_tally.wins_received
            + player_one_tally.losses_received
            + player_one_tally.wins_served
            + player_one_tally.losses_served
            == 10
        )
        assert (
            player_two_tally.wins_received
            + player_two_tally.losses_received
            + player_two_tally.wins_served
            + player_two_tally.losses_served
            == 10
        )

    def test_returns_correct_win_rate_data(self):
        player_one = core_factories.UserFactory(username="player one")
        player_two = core_factories.UserFactory(username="player two")

        match_one = match_tracker_factories.MatchResultFactory(winner=player_one, loser=player_two)
        match_two = match_tracker_factories.MatchResultFactory(winner=player_two, loser=player_one)
        matches = dataclasses.Matches(match_results=[match_one, match_two])

        tally_data = queries.build_tally_data_by_player(matches)
        assert len(tally_data.keys()) == 2

        player_one_tally = tally_data[player_one]
        player_two_tally = tally_data[player_two]
        assert player_one_tally.win_rate == 50
        assert player_two_tally.win_rate == 50

    def test_returns_correct_streak_data(self):
        player_one = core_factories.UserFactory(username="player one")
        player_two = core_factories.UserFactory(username="player two")

        # Build a match history where player one wins three games in a row
        match_one = match_tracker_factories.MatchResultFactory(winner=player_one, loser=player_two)
        match_two = match_tracker_factories.MatchResultFactory(winner=player_one, loser=player_two)
        match_three = match_tracker_factories.MatchResultFactory(
            winner=player_one, loser=player_two
        )
        match_four = match_tracker_factories.MatchResultFactory(
            winner=player_two, loser=player_one
        )
        matches = dataclasses.Matches(
            match_results=[match_one, match_two, match_three, match_four]
        )

        tally_data = queries.build_tally_data_by_player(matches)
        assert len(tally_data.keys()) == 2

        player_one_tally = tally_data[player_one]
        player_two_tally = tally_data[player_two]

        assert player_one_tally.highest_win_streak == 3
        assert player_one_tally.highest_loss_streak == 1

        assert player_two_tally.highest_win_streak == 1
        assert player_two_tally.highest_loss_streak == 3

    def test_returns_correct_last_win_data(self):
        player_one = core_factories.UserFactory(username="player one")
        player_two = core_factories.UserFactory(username="player two")
        player_three = core_factories.UserFactory(username="player three")

        # Build a match history where player one wins three games in a row
        match_one = match_tracker_factories.MatchResultFactory(
            winner=player_one, loser=player_two, played_at=datetime.datetime(2021, 1, 1, 12, 0)
        )
        match_two = match_tracker_factories.MatchResultFactory(
            winner=player_two, loser=player_one, played_at=datetime.datetime(2021, 1, 3, 13, 0)
        )
        match_three = match_tracker_factories.MatchResultFactory(
            winner=player_three, loser=player_one, played_at=datetime.datetime(2021, 1, 15, 13, 0)
        )
        matches = dataclasses.Matches(match_results=[match_one, match_two, match_three])

        tally_data = queries.build_tally_data_by_player(matches)
        assert len(tally_data.keys()) == 3

        player_one_tally = tally_data[player_one]
        player_two_tally = tally_data[player_two]

        assert player_one_tally.last_win_datetime == datetime.datetime(2021, 1, 1, 12, 0)
        assert player_two_tally.last_win_datetime == datetime.datetime(2021, 1, 3, 13, 0)

        with time_machine.travel(datetime.datetime(2021, 2, 1, 14, 0)):
            assert player_one_tally.last_win_days_ago == 31
            assert player_two_tally.last_win_days_ago == 29
