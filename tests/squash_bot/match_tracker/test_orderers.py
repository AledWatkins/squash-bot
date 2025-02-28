import datetime

from squash_bot.match_tracker import orderers
from squash_bot.match_tracker.data import dataclasses

from tests.factories import match_tracker as match_tracker_factories


class TestPlayedAt:
    def test_orders_matches_by_played_at_desc(self):
        match_one = match_tracker_factories.MatchResultFactory(
            played_at=datetime.datetime(2021, 1, 1, 12, 0)
        )
        match_two = match_tracker_factories.MatchResultFactory(
            played_at=datetime.datetime(2021, 1, 1, 13, 0)
        )
        matches = dataclasses.Matches([match_two, match_one])

        ordered_matches = orderers.PlayedAt.order(matches=matches)

        assert ordered_matches == dataclasses.Matches([match_one, match_two])
