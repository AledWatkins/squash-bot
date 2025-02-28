from squash_bot.match_tracker.badges import badge_definitions, queries

from tests.factories import core as core_factories
from tests.factories import match_tracker as match_tracker_factories


class TestDeduplicateBadges:
    def test_deduplicate_crush_badges(self):
        ricky = core_factories.UserFactory(username="ricky")
        steve = core_factories.UserFactory(username="steve")
        match_one = match_tracker_factories.MatchResultFactory(winner=ricky, loser=steve)
        match_two = match_tracker_factories.MatchResultFactory(winner=ricky, loser=steve)
        match_three = match_tracker_factories.MatchResultFactory(winner=steve, loser=ricky)

        crush_1 = badge_definitions.Crush(player=ricky, opponent=steve, badge_earned_in=match_one)
        crush_2 = badge_definitions.Crush(player=ricky, opponent=steve, badge_earned_in=match_two)
        crush_3 = badge_definitions.Crush(
            player=steve, opponent=ricky, badge_earned_in=match_three
        )

        badges = [crush_1, crush_2, crush_3]
        deduped_badges = queries.deduplicate_badges(badges)
        assert len(deduped_badges) == 2

    def test_deduplicate_win_streak_badges(self):
        ricky = core_factories.UserFactory(username="ricky")
        steve = core_factories.UserFactory(username="steve")
        match_one = match_tracker_factories.MatchResultFactory(winner=ricky, loser=steve)
        match_two = match_tracker_factories.MatchResultFactory(winner=ricky, loser=steve)

        win_streak_1 = badge_definitions.WinStreak(
            player=ricky, streak_length=5, badge_earned_in=match_one, is_ongoing=False
        )
        win_streak_2 = badge_definitions.WinStreak(
            player=ricky, streak_length=3, badge_earned_in=match_two, is_ongoing=False
        )

        badges = [win_streak_1, win_streak_2]
        deduped_badges = queries.deduplicate_badges(badges)
        assert deduped_badges == [
            badge_definitions.WinStreak(
                player=ricky, streak_length=5, badge_earned_in=match_one, is_ongoing=False
            ),
        ]
