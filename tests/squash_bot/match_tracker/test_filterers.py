import datetime

from squash_bot.match_tracker import filterers
from squash_bot.match_tracker.data import dataclasses

from tests.factories import match_tracker as match_tracker_factories


class TestLastSessionOrDateFilterer:
    def test_filter_with_date(self):
        match_one = match_tracker_factories.MatchResultFactory(
            played_at=datetime.datetime(2021, 1, 1, 12, 0)
        )
        match_two = match_tracker_factories.MatchResultFactory(
            played_at=datetime.datetime(2021, 1, 2, 12, 0)
        )

        matches = dataclasses.Matches(match_results=[match_one, match_two])

        filtered_matches = filterers.LastSessionOrDate.filter(
            matches=matches,
            date="2021-01-01",
        )

        assert filtered_matches == dataclasses.Matches([match_one])

    def test_filter_with_no_date(self):
        match_one = match_tracker_factories.MatchResultFactory(
            played_at=datetime.datetime(2021, 1, 1, 12, 0)
        )
        match_two = match_tracker_factories.MatchResultFactory(
            played_at=datetime.datetime(2021, 1, 2, 12, 0)
        )
        match_three = match_tracker_factories.MatchResultFactory(
            played_at=datetime.datetime(2021, 1, 2, 13, 0)
        )

        matches = dataclasses.Matches(match_results=[match_one, match_two, match_three])

        filtered_matches = filterers.LastSessionOrDate.filter(matches=matches)

        assert filtered_matches == dataclasses.Matches([match_two, match_three])
