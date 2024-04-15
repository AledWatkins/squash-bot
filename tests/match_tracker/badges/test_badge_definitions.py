from decimal import Decimal

from squash_bot.match_tracker.badges import badge_definitions, queries
from squash_bot.match_tracker.data import dataclasses

from tests.factories import core as core_factories
from tests.factories import match_tracker as match_tracker_factories


class TestCrushCollector:
    def test_finds_crush(self):
        match_one = match_tracker_factories.MatchResultFactory(winner_score=11, loser_score=0)
        match_two = match_tracker_factories.MatchResultFactory(winner_score=11, loser_score=1)
        matches = dataclasses.Matches([match_one, match_two])

        returned_badges = queries.collect_badges(matches=matches, badges=[badge_definitions.Crush])

        assert len(returned_badges) == 1
        assert returned_badges[0] == badge_definitions.Crush(
            player=match_one.winner, opponent=match_one.loser, badge_earned_in=match_one
        )


class TestCleanSweepCollector:
    def test_finds_clean_sweep(self):
        ricky = core_factories.UserFactory(username="ricky")
        steve = core_factories.UserFactory(username="steve")
        karl = core_factories.UserFactory(username="karl")

        match_one = match_tracker_factories.MatchResultFactory(winner=karl, loser=steve)
        match_two = match_tracker_factories.MatchResultFactory(winner=steve, loser=ricky)
        match_three = match_tracker_factories.MatchResultFactory(winner=karl, loser=steve)
        match_four = match_tracker_factories.MatchResultFactory(winner=steve, loser=ricky)
        matches = dataclasses.Matches([match_one, match_two, match_three, match_four])

        returned_badges = queries.collect_badges(
            matches=matches, badges=[badge_definitions.CleanSweep]
        )

        assert len(returned_badges) == 1
        assert returned_badges[0] == badge_definitions.CleanSweep(
            player=karl, badge_earned_in=match_three
        )


class TestWoodenSpoonCollector:
    def test_finds_wooden_spoon(self):
        ricky = core_factories.UserFactory(username="ricky")
        steve = core_factories.UserFactory(username="steve")
        karl = core_factories.UserFactory(username="karl")

        match_one = match_tracker_factories.MatchResultFactory(winner=karl, loser=steve)
        match_two = match_tracker_factories.MatchResultFactory(winner=steve, loser=ricky)
        match_three = match_tracker_factories.MatchResultFactory(winner=karl, loser=steve)
        match_four = match_tracker_factories.MatchResultFactory(winner=steve, loser=ricky)
        matches = dataclasses.Matches([match_one, match_two, match_three, match_four])

        returned_badges = queries.collect_badges(
            matches=matches, badges=[badge_definitions.WoodenSpoon]
        )

        assert len(returned_badges) == 1
        assert returned_badges[0] == badge_definitions.WoodenSpoon(
            player=ricky, badge_earned_in=match_four
        )


class TestWinStreakCollector:
    def test_finds_win_streak(self):
        ricky = core_factories.UserFactory(username="ricky")
        steve = core_factories.UserFactory(username="steve")
        karl = core_factories.UserFactory(username="karl")

        # Create a match history where Karl wins three in a row and then loses
        match_one = match_tracker_factories.MatchResultFactory(winner=karl, loser=steve)
        match_two = match_tracker_factories.MatchResultFactory(winner=steve, loser=ricky)
        match_three = match_tracker_factories.MatchResultFactory(winner=karl, loser=steve)
        match_four = match_tracker_factories.MatchResultFactory(winner=steve, loser=ricky)
        match_five = match_tracker_factories.MatchResultFactory(winner=karl, loser=ricky)
        match_six = match_tracker_factories.MatchResultFactory(winner=steve, loser=karl)
        matches = dataclasses.Matches(
            [match_one, match_two, match_three, match_four, match_five, match_six]
        )

        returned_badges = queries.collect_badges(
            matches=matches, badges=[badge_definitions.WinStreak]
        )

        assert len(returned_badges) == 1
        returned_badge = returned_badges[0]
        assert returned_badge == badge_definitions.WinStreak(
            player=karl, streak_length=3, badge_earned_in=match_five, is_ongoing=False
        )
        # We need to specifically check that the `is_current` attribute is set to True since it's not included in the
        # __eq__ method
        assert returned_badge.is_ongoing is False

    def test_finds_current_streak(self):
        ricky = core_factories.UserFactory(username="ricky")
        steve = core_factories.UserFactory(username="steve")
        karl = core_factories.UserFactory(username="karl")

        # Create a match history where Karl wins three in a row and then loses
        match_one = match_tracker_factories.MatchResultFactory(winner=karl, loser=steve)
        match_two = match_tracker_factories.MatchResultFactory(winner=steve, loser=ricky)
        match_three = match_tracker_factories.MatchResultFactory(winner=steve, loser=ricky)
        match_four = match_tracker_factories.MatchResultFactory(winner=steve, loser=karl)
        matches = dataclasses.Matches([match_one, match_two, match_three, match_four])

        returned_badges = queries.collect_badges(
            matches=matches, badges=[badge_definitions.WinStreak]
        )

        assert len(returned_badges) == 1
        returned_badge = returned_badges[0]
        assert returned_badge == badge_definitions.WinStreak(
            player=steve, streak_length=3, badge_earned_in=match_four, is_ongoing=True
        )
        # We need to specifically check that the `is_current` attribute is set to True since it's not included in the
        # __eq__ method
        assert returned_badge.is_ongoing is True


class TestLossStreakCollector:
    def test_finds_loss_streak(self):
        ricky = core_factories.UserFactory(username="ricky")
        steve = core_factories.UserFactory(username="steve")
        karl = core_factories.UserFactory(username="karl")

        # Create a match history where Karl wins three in a row and then loses
        match_one = match_tracker_factories.MatchResultFactory(winner=karl, loser=steve)
        match_two = match_tracker_factories.MatchResultFactory(winner=steve, loser=ricky)
        match_three = match_tracker_factories.MatchResultFactory(winner=karl, loser=steve)
        match_four = match_tracker_factories.MatchResultFactory(winner=steve, loser=ricky)
        match_five = match_tracker_factories.MatchResultFactory(winner=karl, loser=ricky)
        match_six = match_tracker_factories.MatchResultFactory(winner=steve, loser=karl)
        matches = dataclasses.Matches(
            [match_one, match_two, match_three, match_four, match_five, match_six]
        )

        returned_badges = queries.collect_badges(
            matches=matches, badges=[badge_definitions.LossStreak]
        )

        assert len(returned_badges) == 1
        assert returned_badges[0] == badge_definitions.LossStreak(
            player=ricky, streak_length=3, badge_earned_in=match_five, is_ongoing=True
        )


class TestFirstWinAgainstCollector:
    def test_finds_first_win_against(self):
        ricky = core_factories.UserFactory(username="ricky")
        steve = core_factories.UserFactory(username="steve")
        karl = core_factories.UserFactory(username="karl")

        match_one = match_tracker_factories.MatchResultFactory(winner=karl, loser=steve)
        match_two = match_tracker_factories.MatchResultFactory(winner=steve, loser=ricky)
        match_three = match_tracker_factories.MatchResultFactory(winner=karl, loser=steve)
        match_four = match_tracker_factories.MatchResultFactory(winner=steve, loser=karl)
        matches = dataclasses.Matches([match_one, match_two, match_three, match_four])

        returned_badges = queries.collect_badges(
            matches=matches, badges=[badge_definitions.FirstWinAgainst]
        )

        assert len(returned_badges) == 3
        assert returned_badges == [
            badge_definitions.FirstWinAgainst(
                player=karl, opponent=steve, badge_earned_in=match_one
            ),
            badge_definitions.FirstWinAgainst(
                player=steve, opponent=ricky, badge_earned_in=match_two
            ),
            badge_definitions.FirstWinAgainst(
                player=steve, opponent=karl, badge_earned_in=match_four
            ),
        ]


class TestStreakBreakerCollector:
    def test_finds_broken_streaks(self):
        ricky = core_factories.UserFactory(username="ricky")
        steve = core_factories.UserFactory(username="steve")
        karl = core_factories.UserFactory(username="karl")

        match_one = match_tracker_factories.MatchResultFactory(winner=karl, loser=steve)
        match_two = match_tracker_factories.MatchResultFactory(winner=karl, loser=ricky)
        match_three = match_tracker_factories.MatchResultFactory(winner=karl, loser=steve)
        match_four = match_tracker_factories.MatchResultFactory(winner=steve, loser=karl)
        matches = dataclasses.Matches([match_one, match_two, match_three, match_four])

        returned_badges = queries.collect_badges(
            matches=matches, badges=[badge_definitions.StreakBreaker]
        )

        assert len(returned_badges) == 1
        assert returned_badges == [
            badge_definitions.StreakBreaker(
                player=steve, opponent=karl, streak_length=3, badge_earned_in=match_four
            ),
        ]


class TestMVP:
    def test_finds_mvp(self):
        ricky = core_factories.UserFactory(username="ricky")
        steve = core_factories.UserFactory(username="steve")
        karl = core_factories.UserFactory(username="karl")

        match_one = match_tracker_factories.MatchResultFactory(
            winner=karl, winner_score=11, loser=ricky, loser_score=9
        )
        match_two = match_tracker_factories.MatchResultFactory(
            winner=steve, winner_score=11, loser=ricky, loser_score=0
        )
        match_three = match_tracker_factories.MatchResultFactory(
            winner=karl, winner_score=11, loser=ricky, loser_score=9
        )
        match_four = match_tracker_factories.MatchResultFactory(
            winner=karl, winner_score=11, loser=ricky, loser_score=9
        )
        match_five = match_tracker_factories.MatchResultFactory(
            winner=ricky, winner_score=11, loser=steve, loser_score=0
        )
        matches = dataclasses.Matches([match_one, match_two, match_three, match_four, match_five])

        returned_badges = queries.collect_badges(matches=matches, badges=[badge_definitions.MVP])

        # Karl won 3 games with a 2 point lead so his average point difference is 2
        # Steve won 1 game with an 11 point lead and lost 1 game by an 11 point difference so his average point difference is 0
        # Ricky has a negative average point difference
        assert len(returned_badges) == 1
        assert returned_badges == [
            badge_definitions.MVP(
                player=karl,
                average_point_difference=Decimal("2.00"),
                badge_earned_in=match_four,
            ),
        ]
